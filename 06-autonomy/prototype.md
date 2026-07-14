# Prototype: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 1, the working agent demo

## What it does

Cortex is a PM chief-of-staff agent. Given one task brief ("assemble this week's leadership status
update for Northstar"), it pulls the project's real state and engineering activity, retrieves past
updates for tone, checks team norms and the roadmap, drafts a status update grounded entirely in
what it pulled, and proposes next-sprint stories (capped and queued, never created). An independent
critic then checks every claim against the pulled data before any human sees it. Cortex stops at a
human-in-the-loop checkpoint — the update and stories are **queued for approval, nothing is posted**
— and it escalates instead of acting whenever data is missing, a date is demanded, a bound is hit,
or a prompt-injection is detected.

## How you built it

- **Coding agent:** Claude Code (directed in plain English; I designed the loop, tools, critic, and bounds — the coding agent edited the files).
- **Model + bounds:** `claude-haiku-4-5` · `MAX_ITERATIONS=8` · `COST_CAP_USD=0.50` · `MAX_REVISIONS=2` · `MAX_QUEUE_ITEMS=10`. A full run costs ≈ $0.02.
- **Repo / config:** [`00-build/`](../00-build/) — the loop (`agent.py`), tools (`tools.py`), critic (`critic.py`), prompts (`prompts.py`), and the reproducible evals (`evals.py`).
- **Live link:** _(optional)_

## Screenshots (required, collected M2 to M6)

Real screenshots of *your* Cortex running. Each row lists the exact command that produces it — run
it in your terminal (`cd 00-build`) and screenshot the result.

| # | Screenshot | What it shows | Command to reproduce |
|---|---|---|---|
| 1 | [Shot1.png](Shot1.png) | Happy path: real drafted update + HITL checkpoint (queued, not posted) | `python3 agent.py happy` → ends **DONE, HITL CHECKPOINT** |
| 2 | [Shot2.png](Shot2.png) | Critic rejecting a bad draft (fabricated metric, invented Sev-1, committed date) | `python3 evals.py reject` → **VERDICT: FAIL** |
| 3 | [Shot3.png](Shot3.png) | Grounding: metric withheld → hallucinated number caught as untraceable | `python3 evals.py blind` → **VERDICT: FAIL** (and `CORTEX_BLIND=metric python3 agent.py happy` shows Cortex declining to invent one) |
| 4 | [Shot4.png](Shot4.png) | Jailbreak refused + injection flagged + escalated | `python3 agent.py jailbreak` → **ESCALATE** |
| 5 | [Shot5.png](Shot5.png) | A bound halting a runaway | `CORTEX_MAX_ITERATIONS=1 python3 agent.py happy` → **MAX ITERATIONS reached** (or `CORTEX_COST_CAP_USD=0.001 …`, or `CORTEX_MAX_QUEUE_ITEMS=2 …`) |
| 6 | [Shot1.png](Shot1.png) | End-to-end run (same happy-path trace: tools → draft → critic → HITL) | `python3 agent.py happy` |

### Screenshot gallery

**1. Happy path → DONE, HITL checkpoint** (critic passes all 10 checks; nothing posted)
![Happy path run ending at the HITL checkpoint](Shot1.png)

**2. Critic rejects a fabricated draft** (M3) — `evals.py reject` → VERDICT: FAIL
![Critic rejecting a bad draft](Shot2.png)

**3. Withheld-metric hallucination caught** (M4) — `evals.py blind` → VERDICT: FAIL
![Critic catching an untraceable metric](Shot3.png)

**4. Jailbreak refused + escalated** (M5) — injection flagged, no action taken
![Jailbreak run refused and escalated](Shot4.png)

**5. Iteration bound halts a runaway** (M5) — `MAX ITERATIONS (1) reached. Escalating`
![Iteration cap tripping](Shot5.png)

### The seven anatomy points, and where each is proven

| # | Anatomy | Proven by |
|---|---|---|
| 1 | Loop + definition of done | Screenshot 1/6 (DONE vs ESCALATE banners) + `loop-spec.md` |
| 2 | Read-only tools; no post/create/merge | Tool calls in the trace + `tools.py` registry (no publish tool) |
| 3 | Independent critic with fail-action + revision cap | Screenshot 2 + the revision-cap halt |
| 4 | Iteration bound | Screenshot 5 (`MAX ITERATIONS reached`) |
| 5 | Cost + commitment bound | Cost-cap trip + queue-cap trip (`batch_exceeds_queue_cap`) |
| 6 | HITL checkpoint (queued, never posted) | Screenshot 1 ending |
| 7 | Jailbreak refusal | Screenshot 4 |

## How to run it

```bash
cd 00-build
pip install -r requirements.txt          # anthropic + python-dotenv
cp .env.example .env                      # then paste your ANTHROPIC_API_KEY
python3 agent.py happy                    # the happy path
python3 agent.py missing-data             # stuck / escalate
python3 agent.py jailbreak                # injection refused + escalated
python3 evals.py                          # deterministic critic rejections (M3/M4)
# Trip a bound:
CORTEX_MAX_ITERATIONS=1 python3 agent.py happy
CORTEX_COST_CAP_USD=0.001 python3 agent.py happy
CORTEX_MAX_QUEUE_ITEMS=2 python3 agent.py happy
```
