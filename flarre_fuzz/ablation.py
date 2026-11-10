
"""Ablation: which Bully layers detect which planted bug?

Run:
    python -m flarre_fuzz.ablation
"""

from pathlib import Path

from . import bully, llm, referee, sandbox
from .bugs import GOOD_CODE, bug_variants


SPEC = (Path(__file__).parent / "data" / "spec.txt").read_text(
    encoding="utf-8"
)


def _merge(base: list[dict], extra: list[dict]) -> list[dict]:
    seen = {tuple(p.values()) for p in base}
    return base + [
        p for p in extra
        if tuple(p.values()) not in seen
    ]


def matrix() -> dict:
    """Measure failures detected by each testing-layer configuration."""

    notes: list[str] = []

    llm_profiles = (
        bully.llm_profiles(SPEC, notes=notes)
        if llm.configured()
        else []
    )

    if not llm.configured():
        notes.append("GEMINI_API_KEY not configured; Gemini layer skipped.")

    configs = {
        "boundary only": bully.generate(SPEC, ("boundary",)),
        "random only": bully.generate(SPEC, ("random",)),
        "boundary + random": bully.generate(
            SPEC, ("boundary", "random")
        ),
    }

    if llm_profiles:
        configs["Gemini only"] = llm_profiles

        configs["boundary + random + Gemini"] = _merge(
            configs["boundary + random"],
            llm_profiles
        )

    variants = bug_variants()

    bugs = {
        bug: {
            name: len(
                referee.check(
                    profiles,
                    sandbox.run(code, profiles)
                )
            )
            for name, profiles in configs.items()
        }
        for bug, code in variants.items()
    }

    false_alarms = {
        name: len(
            referee.check(
                profiles,
                sandbox.run(GOOD_CODE, profiles)
            )
        )
        for name, profiles in configs.items()
    }

    return {
        "configs": list(configs),
        "bugs": bugs,
        "notes": notes,
        "llm_profiles": len(llm_profiles),
        "false_alarms": false_alarms,
        "profiles": {
            name: len(profiles)
            for name, profiles in configs.items()
        },
        "llm_measured": bool(llm_profiles),
    }


def run() -> str:
    results = matrix()
    configs = results["configs"]

    lines = [
        "| Planted bug | " + " | ".join(configs) + " |",
        "|---|" + "---|" * len(configs),
    ]

    for bug, row in results["bugs"].items():
        values = [
            f"found ({row[name]})" if row[name] else "MISSED"
            for name in configs
        ]
        lines.append(
            f"| {bug} | " + " | ".join(values) + " |"
        )

    lines.append(
        "| *False alarms on correct code* | "
        + " | ".join(
            str(results["false_alarms"][name])
            for name in configs
        )
        + " |"
    )

    lines.append(
        "| *Profiles generated* | "
        + " | ".join(
            str(results["profiles"][name])
            for name in configs
        )
        + " |"
    )

    if not results["llm_measured"]:
        reason = "; ".join(results["notes"])
        lines.append(
            "\nGemini results not measured: " + reason
        )
    else:
        lines.append(
            f"\nGemini profiles generated: {results['llm_profiles']}"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    output = run()
    print(output)

    Path("ablation_results.md").write_text(
        output + "\n",
        encoding="utf-8"
    )
