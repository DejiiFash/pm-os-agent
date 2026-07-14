# Orchestration Map: Cortex PM Chief-of-Staff Agent

> Module 3 · Orchestration & Subagents, ★ Deliverable 3
>
> Builds on your M2 Loop Spec. Only split one agent into a team when there's a real reason, coordination has a cost.

## 1. Why split? (or why not)

**Default-to-simple check passed with one deliberate split already in place.** Cortex is a single
orchestrator plus **one** subagent — the independent **critic** — and that split earns its keep for
a real reason: *independent validation*. The critic never sees the drafting conversation, so it
can't inherit the drafter's blind spots (this is exactly what caught the fabricated 78% metric in
the M3 rejection run).

Beyond the critic, I add **one more** subagent and stop there: a **GitHub/Jira reader**. Its
justification is *context-window pressure + separation of concerns* — a real activity feed can be
hundreds of raw PRs/issues/comments, and I don't want that flooding Cortex's context or tempting a
hallucinated summary. The reader pages through the raw feed in its own isolated context and returns
a short, **cited** summary. I do **not** add a research/market subagent yet — the weekly-update job
doesn't need it, and unused parallelism is just coordination cost.

## 2. Topology

**Pattern:** single + subagents, sequential.

```
task brief
   │
   ▼
Cortex (orchestrator, M2 loop)
   ├─ delegates → [GitHub/Jira Reader]   bounded: read-only · max N items · returns cited summary
   ├─ reads     →  norms · roadmap · past updates   (read-only tools)
   ├─ drafts the update + calls propose_stories (capped)
   ▼
[Critic ✓]  independent validation · 10 checks · revision cap
   │  (fail → revise, up to MAX_REVISIONS, then escalate)
   ▼
HITL checkpoint → queued for a human · nothing posted
```

## 3. Roster

| Agent / subagent | Responsibility | Runs which Loop Spec |
|---|---|---|
| **Chief-of-staff (Cortex)** | Orchestrates the run and assembles the update | M2 loop |
| **GitHub/Jira reader** | Pages the raw activity feed, returns a cited, compressed summary | Bounded read loop (own item + token cap) |
| **Critic / validator** | Checks the draft against the 10 checks before it advances | Validation loop (revision cap) |
| _Research subagent (deferred)_ | _Market/competitive context — only if a future task needs it_ | _not built_ |

## 4. Communication & hand-offs — and where it plugs into the loop

Only **cited facts** cross a boundary, never a raw dump. Contracts:

- **Cortex → reader:** `{project_id, since, max_items}`
- **Reader → Cortex:** `{summary, cited_items:[{id, title, date}]}` — Cortex may only cite what the reader returned.
- **Cortex → critic:** the draft + the accumulated `source_log`.

**Where it plugs in:** the loop already dispatches every tool through the `TOOLS` registry
(`agent.py`: `result = tools.TOOLS[fn](**args)`). So a subagent plugs in as **one more bounded entry
in that registry** — from Cortex's point of view it's just another tool call, but internally it runs
its own capped loop:

```python
# tools.py — a subagent exposed as a bounded tool
def read_activity_summary(project_id: str, max_items: int = 20) -> dict:
    raw = _load_json("projects.json").get(project_id, {}).get("activity", [])
    raw = raw[:max_items]                      # hard input bound
    # ... its OWN small model call summarizes raw -> cited summary (own token cap) ...
    return {"summary": "...", "cited_items": [{"id": a["id"], "title": a["title"]}
                                              for a in raw if "id" in a]}

TOOLS["read_activity_summary"] = read_activity_summary   # now Cortex can delegate to it
```

No new orchestration machinery in the loop — the seam is the tool registry. (If the reader ever
became a real external service, MCP would be the natural protocol; not needed at this scale.)

## 5. The validator

- **What the critic checks:** correct project/activity · every claim traceable to pulled data ·
  norms compliance · nothing posted/committed · jailbreak refused · bounds respected — plus this
  Cortex's added bar: evidence per RAG call, no hedge words as status, story provenance to the PRD,
  and no unconfirmed commitment (checks 7–10).
- **Fail action:** send the reasons back to Cortex to revise; after `CORTEX_MAX_REVISIONS` (2)
  failed attempts, stop looping and **escalate** to a human (enforced in `agent.py`).

## 6. State: shared vs isolated

- **Shared:** the `source_log` of pulled, cited facts Cortex assembles — the single source of truth
  the critic checks against.
- **Isolated:** each subagent's working context. The reader's raw pagination stays inside the reader
  (only its cited summary returns); the critic's context is isolated by design — it never sees the
  drafting conversation, which is what makes its check independent.

## 7. Cost & latency budget

Each subagent is extra model calls, so each carries its own bound. The **critic** adds ~1 call per
draft and per revision (why the revision cap matters). The **reader** adds ~1 call plus the tokens
of the capped raw feed. Rule: a subagent must return *less* than it consumed (a compressed, cited
summary), or the split isn't paying for itself. Concrete caps → M5 `bounds-and-evals.md`.
