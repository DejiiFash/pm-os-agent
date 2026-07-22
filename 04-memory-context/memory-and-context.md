# Memory & Context: Cortex PM Chief-of-Staff Agent

> Module 4 · Memory & Context, ★ Deliverable 4
>
> Per-source retrieve-vs-include calls defended with the rubric, the retrieval-quality plan, the memory map, and the risks table.

## 1. Context budget

Each loop iteration receives, in priority order: **(1)** the operator rules (`CORTEX_SYSTEM`),
always in context; **(2)** this week's task brief (whole); **(3)** the growing `messages` transcript
of tool calls + results — i.e. only what Cortex has actually pulled. Nothing enters the window that
isn't a standing rule or a real tool result. The design keeps it tight: one project's data, the
matched norm/roadmap slice, and only comparable past updates — not the whole corpus of anything.

## 2. Per-source: retrieve vs. long-context (defended with the rubric)

Rubric factors: **size · volatility · citation/audit · cost · latency.** Deciding factor named.

| Source (tool) | Size / volatility | Decision | Why (deciding factor) |
|---|---|---|---|
| **Task brief** (`get_task`) | one doc / static in a run | **Long-context** | *size* — bounded; reason over the whole thing (as data, not instructions). |
| **Project record** (`get_project`) | small / changes as project moves | **Long-context (include)** | *size* — a single small record; nothing to narrow, so include it whole. |
| **Recent activity** (`get_activity`) | large / grows constantly | **Retrieve** | *size + volatility* — far too big to include; narrow to this project's relevant, current history. |
| **Past updates & decisions** (`search_past_updates`) | large / append-only | **Retrieve** | *size* — unbounded history; pull only the comparable precedents. |
| **Roadmap** (`get_roadmap`) | medium / confidential flags | **Retrieve** | *citation / confidentiality* — pull only the relevant shareable slice; never ship embargoed items (P-ORBIT). |
| **Team norms / playbook** (`get_norms`) | medium / must stay current | **Retrieve** | *citation* — cite the exact rule that applies; don't ship the whole playbook every turn. |

## 3. Retrieval quality plan (agentic retrieval, not naive RAG)

For every *retrieved* source, the moves its failure mode demands (at minimum, **grade** what comes
back — an unchecked row is naive RAG, the thing that made Cortex hallucinate in A1):

| Retrieved source | Routing | Grading | Reranking | Self-verify | Caching |
|---|:-:|:-:|:-:|:-:|:-:|
| `get_activity` | ✓ | ✓ | ✓ | · | · |
| `search_past_updates` | ✓ | ✓ | · | · | ✓ |
| `get_roadmap` | ✓ | ✓ | · | ✓ | ✓ |
| `get_norms` | ✓ | ✓ | · | ✓ | ✓ |

- **Routing** — Cortex picks the tool per question (activity for status, past-updates for tone, roadmap/norms for rules).
- **Grading** — drop plausible-but-irrelevant hits before they reach context (`search_past_updates` filters by keyword overlap).
- **Reranking** — for the activity feed, surface the most recent/relevant items when recall is fine but the right one is buried.
- **Self-verify** — the ★ backbone: the independent **critic** checks every claim traces to the pulled `source_log`; essential on roadmap/norms where a wrong answer is costly (a leak or a policy breach). Proven: withhold the metric (`CORTEX_BLIND=metric`) and a fabricated "41%" is caught as *not traceable*.
- **Caching** — slow-changing roadmap/norms/precedent reads are the cache candidates under cost/latency pressure.

## 4. Memory map (the four stores)

| Type | What Cortex stores | Lifetime |
|---|---|---|
| **Working** | the activity + metrics pulled for *this run's* update — **including volatile status** (re-pulled every run, never stored) | this run only |
| **Episodic** | prior interactions with this project / thread (past updates, decision log) | per-thread; ages out |
| **Semantic** | durable facts: product **names**, **requirements**, approval routing, standing norms | long-lived; updated deliberately |
| **Shared** | findings a subagent (the critic) hands back to the drafting loop | scoped to the collaboration |

> Design note: development **status** is *volatile*, so it lives in **Working (re-pull each run)**,
> never in Semantic — storing it is how a "GREEN, on track" from last month gets reused after it's
> false.

## 5. Memory risks & mitigations

| Risk | Where it bites | Mitigation |
|---|---|---|
| **Drift** | stored project terms diverge from reality | source validation; refresh cadence; the critic re-checks claims vs. freshly pulled data each run |
| **Poisoning** | a bad fact from a message/brief gets stored and trusted | validate before write; track provenance; first-party sources only; injections refused + escalated |
| **Staleness** | a policy/metric/benchmark changed; memory still cites the old one (e.g. a pricing benchmark, or last week's status) | **TTL + re-fetch volatile facts** — never carry status/metrics across runs |
| **PII / retention** | confidential/PII data over-stored or over-reachable | TTL + scoping; store the minimum; CONFIDENTIAL roadmap (P-ORBIT) never enters an external/company-wide context |

> Tie-back: what each decision may read/write is part of the **Agent Line (M1)**; the TTL / retention
> / scope numbers become enforced **Bounds in M5**.

## For #cohort-channel

**Trickiest retrieve-vs-long-context call:** the **project record** (`get_project`). I went back and
forth — it *feels* like a big historical thing you'd retrieve, but the rubric factor that settled it
was **size**: it's a single small record with nothing to slice, so you **include** it whole.
(Honorable mention: roadmap flipped from include → retrieve because **confidentiality** forces you to
pull only the shareable slice.)

---

**Grounding, proven (B4 runs):** grounded → cites `#812` and `39% → 41%` from pulled data; withheld
`get_activity` → Cortex **escalates instead of inventing**, and if a number is fabricated anyway the
critic catches it as untraceable. Two independent defenses — the retrieval plan doing its job.
