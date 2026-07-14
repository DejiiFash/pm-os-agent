# Build Insights: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 4, what you learned building it
>
> _Draft grounded in the real build — edit into your own voice._

## Friction

- **Provider swap.** The starter shipped for OpenAI; I moved it to Claude. The real friction wasn't
  the model, it was the plumbing: tool schemas in a different shape, and no built-in JSON mode for
  the critic (I used a response prefill instead). Lesson: the agent's *scaffolding* is where the
  work is, not the prompt.
- **A cap that wouldn't trip.** Setting `MAX_ITERATIONS=2` didn't halt the loop — my Cortex batches
  all its tool pulls into one turn and just *finished*. It only tripped at `=1`. That was the most
  useful surprise of the whole build (see aha).
- **Model variance at the queue cap.** Sometimes Cortex proposed a 4-story batch and hit the cap
  cleanly; sometimes it escalated earlier on a different reason. Non-determinism is real, and a demo
  has to account for it.

## Learning

1. **Capability is not permission — and the strongest place to enforce that is infrastructure, not
   the prompt.** Cortex can't post because there is *no post tool*, not because I asked it nicely. A
   missing function can't be jailbroken.
2. **Grounding has two independent layers.** A well-grounded agent declines to state data it can't
   see; and if it invents something anyway, an *independent* critic that only sees the pulled data
   catches it. Neither layer alone is enough.
3. **A bound only matters when it's set below what the task actually needs.** Headroom you never hit
   isn't a bound, it's decoration.

## Aha moment

The `MAX_ITERATIONS=2` non-trip. I'd been thinking of bounds as safety numbers you set high and
forget. Watching the cap *fail to fire* because the agent was efficient made it click: a bound is a
statement about how many turns the task legitimately needs, and you only learn that by watching real
runs. Bounds are empirical, not decorative.

## What you'd do differently

- Build the **GitHub/Jira reader subagent** for real (I only sketched it in M3), so activity comes
  from a live, bounded source instead of a fixture.
- Add a **wall-clock timeout** bound — today only iteration and cost caps limit runtime; a hung tool
  call could still stall a run.
- Make `propose_stories` behavior more **deterministic** so the commitment-cap demo fires the same
  way every time (e.g., always attempt the full PRD-justified batch before escalating).
