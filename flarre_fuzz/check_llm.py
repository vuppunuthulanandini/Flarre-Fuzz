
"""
Verify Gemini API connectivity and measure the LLM layers.

Run:
    python -m flarre_fuzz.check_llm
"""

import sys
from pathlib import Path
from . import ablation, bully, llm, orchestrator


DATA = Path(__file__).parent / "data"
SPEC = (DATA / "spec.txt").read_text(encoding="utf-8")


def step(ok: bool, msg: str) -> bool:
    print(("  [ok]   " if ok else "  [FAIL] ") + msg)
    return ok


def main() -> int:
    print(f"Flarre-Fuzz Gemini LLM check (model: {llm.model()})")

    # Step 1: Check whether the Gemini API key is configured
    if not step(
        llm.configured(),
        "GEMINI_API_KEY is set (environment variable or .env file)"
    ):
        print(
            "\n  -> Create a .env file in the project root with:"
            "\n     GEMINI_API_KEY=your-google-api-key"
            "\n     FLARRE_MODEL=gemini-3.8-flash"
        )
        return 1

    # Step 2: Test actual Gemini API authentication
    try:
        reply = llm.complete(
            "Reply with exactly: OK",
            max_tokens=10
        )

        if not reply.strip():
            raise RuntimeError("Gemini returned an empty response")

        step(
            True,
            f"Gemini API call succeeded (reply: {reply.strip()[:20]!r})"
        )

    except Exception as e:
        step(False, f"Gemini API call failed: {llm.describe(e)}")
        print(
            "\n  -> Check your API key, API quota, model availability "
            "and internet connection."
        )
        return 1

    # Step 3: Test Gemini-generated adversarial customer profiles
    print("\n[1/4] Testing Gemini Bully...")

    notes: list[str] = []

    try:
        profiles = bully.llm_profiles(SPEC, notes=notes)

        step(
            bool(profiles),
            notes[-1] if notes else "Gemini Bully generated profiles"
        )

        if not profiles:
            print("  -> No LLM-generated profiles returned.")
        else:
            probes = sorted({
                p["age"]
                for p in profiles
                if p["age"] in (24, 25, 26, 29, 30, 69, 70)
            })

            print(
                f"         Threshold ages tested by Gemini: {probes}"
            )
            print(
                f"         Total Gemini profiles generated: {len(profiles)}"
            )

    except Exception as e:
        step(False, f"Gemini Bully failed: {llm.describe(e)}")
        return 1

    # Step 4: Test the complete adversarial testing pipeline
    print("\n[2/4] Testing complete Flarre-Fuzz pipeline...")

    try:
        target_code = (DATA / "target.py").read_text(encoding="utf-8")

        result = orchestrator.run_scan(
            target_code,
            SPEC,
            layers=("boundary", "random", "llm")
        )

        step(
            True,
            "Full adversarial scan completed"
        )

        print(
            f"         Profiles tested: {result.get('profiles_tested', 'N/A')}"
        )

        print(
            f"         Initial failures: {len(result['initial_failures'])}"
        )

        print(
            f"         Remaining failures: {len(result['remaining_failures'])}"
        )

        patch_source = result["patch_source"]

        step(
            patch_source == "llm",
            f"Fixer source: {patch_source}"
        )

        if patch_source != "llm":
            print(
                "  -> The repair did not come from a live Gemini-generated patch."
            )

        for note in result["notes"]:
            print("         Note:", note)

    except Exception as e:
        step(False, f"Pipeline failed: {llm.describe(e)}")
        return 1

    # Step 5: Run measured ablation experiment
    print("\n[3/4] Running ablation experiment...")

    try:
        output = ablation.run()

        print(output)

        Path("ablation_results.md").write_text(
            output + "\n",
            encoding="utf-8"
        )

        step(
            True,
            "Ablation results saved to ablation_results.md"
        )

    except Exception as e:
        step(False, f"Ablation experiment failed: {llm.describe(e)}")
        return 1

    print("\n[4/4] Gemini integration check completed.")

    print("\n" + "=" * 55)
    print("FLARRE-FUZZ GEMINI DIAGNOSTICS FINISHED")
    print("=" * 55)

    return 0


if __name__ == "__main__":
    sys.exit(main())
