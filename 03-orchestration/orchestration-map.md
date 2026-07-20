# Orchestration Map: Cortex PM Chief-of-Staff Agent

> Module 3 · Orchestration & Subagents, ★ Deliverable 3
>
> Builds on your M2 Loop Spec. Only split one agent into a team when there's a real reason, coordination has a cost.

## 1. Why split? (or why not)

**Current design (from M2):** a hook loop — triggered by an inbound PM task, Cortex drafts a
leadership update and proposes a capped batch of stories, then stops for PM review.

**Default-to-simple check — score the four reasons to split:**

| Reason to split | Applies? | Why / why not |
|---|---|---|
| **Separation of concerns** | **No** | Pulling data + drafting is one coherent job; there's no concrete contamination to isolate. |
| **Parallelism** | **No** | One weekly update assembled in sequence — no real wall-clock time to save. |
| **Independent validator** | **Yes** | Cortex produces drafts and story proposals a human must trust. A separate critic that *didn't write the draft* can't inherit its blind spots — the cleanest, most defensible split. |
| **Context-window pressure** | **No (today)** | The activity feed is small enough to reason over directly. If a real GitHub/Jira feed grew to hundreds of items, a bounded read-only "reader" subagent would earn its place — noted as a future split, not built now. |

**The call:** Cortex stays a **single drafting agent + exactly one subagent — the independent
critic.** One reason held (independent validation); the rest would be splitting to look
sophisticated, which the lab (rightly) warns against.

## 2. Topology (+ text diagram)

**Pattern:** single + subagents (sequential).

```
[Inbound PM task]
        │
        ▼
    [Cortex] ── reads ──> internal data tools (project, activity, past updates, roadmap, norms)
        │  drafts update / preps story proposals
        ▼
   [Validator] ── fail ──> back to Cortex (max 2 revisions) ──> escalate to PM
        │  pass
        ▼
   [PM review checkpoint] ──> approve / send
```

## 3. Agents / subagents roster

| Name | Responsibility | Model tier | Loop spec it runs |
|---|---|---|---|
| **Cortex** | Draft status updates, pull internal data, prep story proposals | Fast (`claude-haiku-4-5`) | M2 hook loop (`02-loop-design/loop-spec.md`) |
| **Validator (critic)** | Independently check Cortex's output against the Step 2 checks | Fast (`claude-haiku-4-5`), **separate call/context** | Short goal loop: check → pass/fail → stop |

## 4. Communication & hand-offs

- **Cortex → Validator:** the drafted update (or story proposal) **+ the source data it used**, as structured text (the `source_log`).
- **Validator → Cortex:** **pass/fail + the list of failed checks** (specific reasons, so the revision is targeted).
- **Validator → PM:** on escalate, the item routes to the PM with the failure flagged.
- **Protocol:** a plain in-process hand-off is used. MCP / A2A are **optional and not required** at this scale.

## 5. The validator (checks + fail-action + revision cap)

- **What it checks (concrete, not fuzzy):**
  1. References the correct project and real PR / issue IDs from pulled data.
  2. Every figure/metric/date is traceable to pulled data — **no invented numbers**.
  3. The proposed story batch stays within the queue cap (`CORTEX_MAX_QUEUE_ITEMS`), or flags that it exceeds it.
  4. Tone matches team norms with **no commitments Cortex isn't allowed to make** (ship/GA dates, launch gates).
  5. Nothing is posted/committed and no CONFIDENTIAL roadmap item leaks; injections are refused.
- **Fail-action:** **Revise** — return the draft to Cortex with the specific failed checks noted.
- **Revision cap:** **max 2 revisions**, then **escalate to the PM** (never loop forever).
- **Pass-action:** the item advances to the **PM review checkpoint** — it does **not** auto-send (still above the agent line from M1).

*Built & proven:* these checks live in `CRITIC_SYSTEM` (`00-build/prompts.py`); the loop runs the
critic after each proposed output and bounces a fail back up to `CORTEX_MAX_REVISIONS` in
`00-build/agent.py`. See the rejection screenshot in `06-autonomy/prototype.md` (a fabricated 78%
metric + a committed GA date → **VERDICT: FAIL**).

## 6. Shared vs. isolated state

- **Shared:** the project thread + the cited source data + the draft — both agents can see these (the `source_log` is the single source of truth the critic checks against).
- **Isolated:** each agent's own scratch reasoning. The **validator never sees Cortex's drafting conversation** — only the draft + source data — which is exactly what keeps its check independent (it can't inherit the drafter's blind spots). Each model call has its own credential/context.

## 7. Cost & latency budget

- **Extra model calls:** the validator adds **~1 call per proposed item**. Worst case with the revision cap: **3 critic calls** (initial + 2 revisions) plus the extra drafter calls for each revision.
- **Rough ceiling:** a full run is **~8k tokens, under $0.05**, and **under ~30s** end-to-end including one revision (observed runs land around **$0.02–0.05**).
- **The rule:** a subagent must earn its coordination cost. The critic does — one cheap extra call buys an independent trust check. This budget becomes an enforced **bound in M5** (`05-bounds-evals/bounds-and-evals.md`): the revision cap and cost cap are what keep the worst case bounded.

## For #cohort-channel

**Validator fail-action:** *revise* — the critic returns the draft to Cortex with the specific
failed checks named, Cortex gets **up to 2 revision passes**, then it **escalates to the PM**. So a
stuck draft never loops forever: after two failed attempts a human takes over, and nothing reaches
the PM as "approved" until it either passes the critic or is explicitly escalated.
