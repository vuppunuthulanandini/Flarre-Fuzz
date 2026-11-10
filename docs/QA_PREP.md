# Tough questions and honest answers

**Why not just paste the code into ChatGPT?**
An LLM can draft or explain, but it can hallucinate and nobody can prove its answer correct. Here it only creates and explains.
Judging is plain code (repeatable), every fix is re-run against the whole suite, a human approves, and everything is logged.

**How does the Referee know what is correct?**
Two ways: invariants that must always hold (premium positive and capped, more claims never cheaper, discount cap) and a trusted
reference implementation of the written spec. If those are wrong, the verdicts are wrong, so a human reviews them.

**Doesn't Flarre already have a Testing Agent?**
Yes, and I don't know its internals. This is designed as a complementary adversarial layer: its only job is to break code with
rare and extreme cases. It does not replace engineers or the existing agent.

**Isn't fuzzing an old idea?**
Yes. The contribution is the combination for this domain: spec-aware attack layers, a deterministic judge, failure shrinking
tied to spec clauses, re-verified fixes, a human gate and an audit trail.

**What is actually proven so far?**
On a toy calculator with five planted bugs, the deterministic layers find all five with zero false alarms, and the ablation shows
which layer misses what. The LLM layers are built and validated but not yet measured.

**Why is the sandbox only a subprocess?**
It is a stand-in for a system clone, fine for a local demo. Production would use containers and network isolation.

**Why plain Python instead of LangGraph?**
The flow is a short loop with a retry limit, so a framework would add weight without value. It maps directly onto a LangGraph
state graph (conditional retry edge, human-approval pause) when it needs to scale.

**Why TF-IDF and not embeddings?**
The spec has seven clauses; TF-IDF is enough and dependency-free. For a large rulebook I would use embeddings and a vector DB.

**What if the LLM writes a wrong patch?**
It must parse and keep the function signature, the entire suite re-runs on it (max 3 attempts), and a human approves.

**What would you build next?**
Measure the LLM layers across runs, add more rule sets, container isolation, durable workflows, and a vector DB.
