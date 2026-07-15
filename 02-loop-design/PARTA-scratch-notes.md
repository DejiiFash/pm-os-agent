# Module 2 · Part A — SCRATCH NOTES (not the deliverable, do NOT commit)

> Rough, by-instinct draft of Cortex's loop, written BEFORE the lecture.
> The real loop-spec.md gets built in Part B.

## My first instinct (came out as an email assistant)
1. Start: whenever I get an email
2. Done: review the email + recommend a response I can accept or modify; if I accept, respond automatically
3. Stop if: the email is urgent
4. Needs: connect to all my Gmail accounts

## Same instinct, mapped to Cortex (the PM agent)
1. **Start** — when a PM task/brief lands (e.g. "assemble this week's leadership update").
   Open question I'm holding: is that a "when something happens" trigger or a "on a clock" trigger?
2. **Done (one run)** — a status update + proposed stories are drafted and QUEUED for my
   approval. Cortex stops there; it does NOT post on its own (a human posts).
3. **Stop / hand off to a human when:**
   My instincts (came out as email, map to Cortex):
   - it's **urgent / high-stakes**
   - it's **noise that needs no action** (a marketing/broadcast email → an ask that needs no update)
   - it **can't get the data** it needs
   - it **seems fishy** (someone trying to trick it → prompt injection → refuse + escalate)
   Extras to consider:
   - it'd have to **promise a date/commitment it can't verify** → escalate the date question
   - there's a **critical blocker (Sev-1)** → escalate the go/no-go, don't report all-clear
   - the ask would **exceed a limit** (too many stories at once) → stop, don't game the cap
   - it's about to do something **public/irreversible** (post company-wide) → always stop for approval
   - it's **stuck** (tried several times / spent too much without finishing) → stop and hand off
   - it **can't back a claim with real data** → stop rather than invent
4. **Needs (tools/data):** project state, recent engineering activity, past updates,
   roadmap, team norms — plus a way to propose stories (queued, capped).

## The one question I'm most unsure about (A4 — holding for the lecture)
> My email instinct said "if I accept, respond automatically" — but Cortex never
> auto-sends, it stops at "queued." **When is auto-acting OK vs. not?**

(Hunch: it's the same thing as my M1 agent line — reversibility / blast radius /
measurability. Auto-act when a mistake is cheap to undo and low-stakes; stop for a
human when it's irreversible or high blast radius. Want the lecture's real answer.)
