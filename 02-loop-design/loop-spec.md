# Loop Spec: Cortex PM Chief-of-Staff Agent

> Module 2 · Loop Engineering, ★ Deliverable 2
>
> Your one-page blueprint for how the work you handed to the agent (M1) actually *runs*.
> An agent is just a prompt that fires itself, this spec says when it fires, what "done" means, and what it needs to do the job. Living document; refine as the course progresses.

## 1. Trigger & loop type

**Chosen type: Hook (event-driven) + cron daily-sweep backup.**

- **Hook** on an inbound PM task (e.g. "assemble this week's leadership update"). Inbound tasks
  are *events*, so a hook gives the fastest, cheapest response — Cortex reacts the moment a task
  lands, no wasted work.
- **Cron sweep at 09:00 local** as the safety net: a hook can silently miss an event (a dropped
  webhook, a task posted while the system was down). The daily sweep re-scans for anything
  unhandled so nothing falls through.

**Why not the others:**
- *Not a pure heartbeat* — polling "anything new?" on a cadence is wasteful when tasks already emit
  events we can hook. (Use a heartbeat only when the source can't emit events.)
- *Not a pure goal loop* — drafting a weekly update has a clear, bounded definition of done
  ("draft written + queued"), not an open-ended outcome to chase until validated. You earn a goal
  loop; this isn't one.

**Idempotency / dedupe:** if the same task fires the hook twice, Cortex must not draft two updates.
Dedupe by **message/task ID** — Cortex records handled IDs and skips repeats (see State).

## 2. Goal / definition of done

A **status update grounded in real pulled activity** plus, when asked, a **capped batch of
proposed stories**, written and **queued for human approval** — the independent critic passes and
**nothing has been posted or committed**. Cortex ends its output with `DONE:`; the loop reads that
marker (`final_signal()` in `agent.py`) and prints the **DONE, HITL CHECKPOINT** banner. Cortex
never sends.

**Self-validation (what proves "done"):** an **independent critic subagent** (not Cortex grading
its own draft) checks that every claim traces to pulled data and matches posting norms before the
draft is queued.

## 3. Stop conditions (all three exits)

| Exit | Detectable trigger | What happens |
|---|---|---|
| **✅ Success** | Draft + any stories ready (batch under the cap), critic returns `pass`, nothing posted; ends `DONE:` | **DONE, HITL CHECKPOINT** — queued for human review |
| **🔁 Stuck / give up** | Required data can't be pulled, the critic keeps rejecting, or no progress — caught by hard counts: `MAX_ITERATIONS=8`, `MAX_REVISIONS=2` (and the cost cap) | Hard halt → **stop, log, and escalate** — enforced in code, outside the model |
| **🙋 Escalate to human** | Embargoed/CONFIDENTIAL project referenced, a public GA-date/commitment demanded, an open Sev-1, a story batch over the cap, or a prompt-injection ("fishy") in the brief; ends `ESCALATE:` | **ESCALATE** banner — Cortex hands off, drafts/posts/commits nothing |

## 4. State

- **Per-run (working):** the `messages` transcript (brief → tool calls → results → draft) and a
  `source_log` of everything pulled, handed to the critic so every claim is checkable.
- **Across runs:** **handled task IDs** (for dedupe), plus roadmap / team norms / past updates as
  read-only ground truth. Scope: **per-project**, retained ~30 days. CONFIDENTIAL roadmap items are
  never written into an external/company-wide update — no cross-project leakage.

## 5. The five components (filled for Cortex)

| Component | For Cortex |
|---|---|
| **Work tree** (isolated workspace per run) | A per-task scratch space (in-memory `messages` + `source_log`); each run is isolated so two project threads never cross-contaminate, and nothing persists to the world. |
| **Skills** (reusable capabilities) | `summarise-activity`, `lookup-project-history`, `draft-status-update`, `propose-stories` (capped). |
| **Plugins / connectors** (tools + access — the M1 agent line made real) | **Read-only:** `get_project`, `get_activity`, `search_past_updates`, `get_roadmap`, `get_norms`. **Queue-only:** `propose_stories`. **No** send / post / create / merge / commit connector exists. **Read-only additional source (design extension, not in the current run):** a **Gmail connector across all the PM's accounts** — pull project-relevant email context as extra activity, **read-only, never send** (stays below the agent line; scoped to project-relevant mail in practice). |
| **Subagents** (delegated validation) | The independent **policy/grounding critic** (`critic.py`) confirms a draft is grounded and matches posting norms before it's queued. → deeper in M3 `orchestration-map.md`. |
| **State tracking** | Handled task IDs (dedupe), iteration + revision counters, and a running cost estimate (`Bounds`) that can trip the cap mid-run. Scope: per-project, ~30 days. |

## 6. Context plan

Each iteration **writes** the latest tool results into `messages` so Cortex reasons over what it
actually pulled, never invented context. It **selects** narrowly — one project's data, only
keyword-matching past updates. It **compresses** large sources into cited summaries (the future
Gmail/activity reader returns a cited digest, not the raw feed). It **isolates** the critic's
context: the critic never sees the drafting conversation, only the draft + `source_log`, which is
what makes its check independent. Full depth → M4.

## 7. Hand-off to bounds & evals

→ M5 `bounds-and-evals.md`. Current values: `CORTEX_MAX_ITERATIONS=8`, `CORTEX_MAX_REVISIONS=2`,
`CORTEX_COST_CAP_USD=0.50`, `CORTEX_MAX_QUEUE_ITEMS=10`. Each will be chosen and justified in M5,
then tripped on purpose to prove it halts.

## For #cohort-channel

- **Which stop condition keeps commitments safe?** The **escalate** exit — it catches exactly the
  cases where a wrong move can't be undone (a public date, an embargoed leak, an over-cap batch)
  and hands them to a human *before* anything is drafted or sent.
- **What changes if Cortex could post under a threshold?** The safety burden shifts from "a human
  approves everything" to the **threshold definition + the validator**: the critic (and a hard
  bound) would have to be trustworthy enough that auto-posting *below* the threshold stays low blast
  radius and reversible, with every above-threshold case still escalating. The agent line moves, so
  the eval bar rises to match.

## Link to live loop

[`00-build/agent.py`](../00-build/agent.py) — the loop, the `final_signal()` definition of done,
and every bound are readable end to end in that one file.
