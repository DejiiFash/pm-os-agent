# Loop Spec: Cortex PM Chief-of-Staff Agent

> Module 2 · Loop Engineering, ★ Deliverable 2
>
> Your one-page blueprint for how the work you handed to the agent (M1) actually *runs*.
> An agent is just a prompt that fires itself, this spec says when it fires, what "done" means, and what it needs to do the job. Living document; refine as the course progresses.

## 1. Trigger & loop type

**Chosen type:** **goal** loop (one PM task brief in → prepared work out), with a **cron**
front-end in production.

Cortex runs to satisfy a single goal: "prepare this PM task for human approval." Today it's
triggered manually per brief (`python agent.py <task>`). In production the natural trigger is a
**Monday-morning cron** that assembles the weekly leadership update, plus a **hook** on a new PRD
to propose next-sprint stories. It's a goal loop (not a heartbeat) because each run has a concrete
done-state a validator can check, not an open-ended "keep watching."

## 2. Goal / definition of done

A **status update grounded in real pulled activity** plus, when asked, a **capped batch of
proposed stories** — the independent critic passes, and **nothing has been posted or committed**.
The run stops at the HITL checkpoint and Cortex ends its output with `DONE:`. The loop reads that
marker (`final_signal()` in `agent.py`) and prints the **DONE, HITL CHECKPOINT** banner.

## 3. Stop conditions

| Condition | What it looks like | What happens |
|---|---|---|
| **Success** | Draft update + any proposed stories ready, critic returns `pass`, nothing posted; Cortex ends with `DONE:` | **DONE, HITL CHECKPOINT** — queued for human review |
| **Escalate to human** | Missing data (project not found), a firm/public date or commitment demanded, an open Sev-1, a prompt-injection in the brief, or a batch over the queue cap; Cortex ends with `ESCALATE:` | **ESCALATE** banner — Cortex stops and hands off, posts/commits nothing |
| **Stuck / give up (bounds)** | Cost cap hit, revision cap hit (critic keeps rejecting), or max iterations reached | Hard halt + escalate — enforced in code, outside the model |

## 4. State

Per-run: the `messages` transcript (brief → tool calls → tool results → draft) and a `source_log`
of everything Cortex pulled, which is handed to the critic so every claim is checkable. Across
runs: the roadmap, team norms, and past updates persist as read-only ground truth (fixtures);
CONFIDENTIAL roadmap items are never written into an external/company-wide update, so there is no
cross-project confidential leakage.

## 5. The five things every loop needs

| Component | For Cortex |
|---|---|
| **Work tree** (isolated workspace per run) | Single process, in-memory `messages` list; each run is isolated and nothing persists to the world (no writes, no publish). |
| **Skills** (reusable capabilities) | Pull project state/activity, retrieve precedent, draft a grounded update, propose a capped story batch. |
| **Plugins / connectors** (tools & access) | `get_project`, `get_activity`, `search_past_updates`, `get_roadmap`, `get_norms` (all read-only) · `propose_stories` (queue only). **No** post/create/merge/commit tool exists. |
| **Subagents** (delegated / validation) | The independent **critic** (`critic.py`) validates every draft before a human sees it. → deeper in M3 `orchestration-map.md`. |
| **State tracking** | Iteration counter, revision counter, and a running cost estimate (`Bounds`) that can trip the cap mid-run. |

## 6. Context plan

Each iteration appends the latest tool results to `messages` so Cortex reasons over what it has
actually pulled, never invented context. The `source_log` accumulates every tool result and is
passed to the critic (which never saw the drafting conversation) so it can trace each claim.
Roadmap and norms are returned whole so Cortex can cite the exact rule/line it relied on. Full
context strategy (write / select / compress / isolate) → M4.

## 7. Hand-off to bounds & evals

→ M5 `bounds-and-evals.md`. Current values: `CORTEX_MAX_ITERATIONS=8`, `CORTEX_MAX_REVISIONS=2`,
`CORTEX_COST_CAP_USD=0.50`, `CORTEX_MAX_QUEUE_ITEMS=10`. Each will be chosen and justified in M5,
then tripped on purpose to prove it halts.

## Link to live loop

[`00-build/agent.py`](../00-build/agent.py) — the loop, the `final_signal()` definition of done,
and every bound are readable end to end in that one file.
