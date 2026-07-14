# Memory & Context: Cortex PM Chief-of-Staff Agent

> Module 4 · Memory & Context

## 1. Context budget

Each loop iteration receives, in priority order: **(1)** the operator rules (`CORTEX_SYSTEM`) —
non-negotiable, always in context; **(2)** the task brief; **(3)** the growing `messages`
transcript of tool calls + their results (what Cortex has actually pulled so far). You can't fit
"everything," so the design pulls narrowly: only the *one* project in question, norms and roadmap
returned whole (small, bounded fixtures), and precedent limited to keyword-matching past updates.
The rule of thumb: rules and freshly-pulled evidence beat volume — nothing enters context that
isn't either a standing rule or a real tool result.

## 2. Retrieve vs. long-context: per source

| Source | Size / volatility | Decision | Why |
|---|---|---|---|
| **Roadmap** | large, slow-changing | Retrieve (returned whole in the mock) | In prod, slice to the relevant item; always respect CONFIDENTIAL flags so embargoed items never reach an external update. |
| **GitHub/Jira activity** | large, changing | **Retrieve** | `get_activity` pulls one project's feed on demand; in prod a bounded reader subagent (see M3) returns a cited summary, not the raw dump. |
| **This week's task brief** | bounded | Long-context | Reason over the whole thing — but as *data*, not instructions (injection defense). |
| **Team norms / playbook** | bounded | Long-context | Returned whole so Cortex can cite the exact rule it relied on. |
| **Past updates / decisions** | growing, changing | **Retrieve** | `search_past_updates` returns only keyword-matching precedent, not the entire history. |

## 3. Retrieval quality plan

- **Routing:** Cortex chooses the tool per need — `get_activity` for current status, `search_past_updates` for tone/precedent, `get_roadmap`/`get_norms` for rules.
- **Document grading:** `search_past_updates` filters by keyword overlap, so irrelevant precedent is dropped before it reaches context (only matching entries return).
- **Reranking:** not needed at this corpus size; a forward hook if the memory store grows.
- **Self-verification:** ★ the heart of M4 — the **critic** independently checks that every claim in the update traces to the pulled `source_log`, and rejects anything that doesn't. Proven in the M4 run: with the activation metric withheld (`CORTEX_BLIND=metric`), a fabricated "41%" is caught as *"not traceable to source data."*
- **Caching:** fixtures are static here; in prod, slow-changing project/roadmap reads are the cache candidates.

## 4. Memory map (your PM brain)

| Memory type | What Cortex stores | Scope / TTL |
|---|---|---|
| **Working** (in-loop) | the `messages` transcript + `source_log` of pulled facts | this run only; purged after |
| **Episodic** (past runs) | past status updates + decision log, via `search_past_updates` | prior weeks, read-only precedent |
| **Semantic** (durable facts/prefs) | team norms / playbook + roadmap facts | durable; the rules that always govern |
| **Shared** (across agents) | the `source_log` handed to the critic | the only thing crossing the Cortex → critic boundary |

## 5. Memory risks & mitigations

| Risk | Mitigation |
|---|---|
| **Drift** | The critic re-checks every claim against freshly pulled data each run; no unverified state is carried forward between runs. |
| **Poisoning** | Brief and note content is treated as *data, not instructions* — injection attempts are refused and escalated (M5 jailbreak run); the search corpus is trusted internal fixtures. |
| **Staleness** | Activity is pulled fresh each run; past-update numbers stay clearly dated and attributed (e.g. the *37% → 39%* precedent is shown as prior-week, never restated as this week's number). |
| **Confidential / retention** | Roadmap items flagged CONFIDENTIAL never enter an external/company-wide update; per-run working context is purged; no cross-project leakage. |

---

**Grounding, proven (M4 runs):** Layer 1 — with a source withheld, Cortex *declines* to state the
number it can't see (grounding held). Layer 2 — if a number is invented anyway, the critic catches
it as untraceable. Two independent defenses, not one.
