"""Cortex, a minimal, explicit agent loop you (and your coding agent) can read end
to end. This is the agent you ship: your PM chief-of-staff. You build it by
directing your coding agent (Claude Code / Cursor / Codex) to shape this file. You
never have to hand-write it.

Every bound the course talks about is visible right here in code, not buried in a
framework: the max-iteration counter, the cost cap, the revision cap, the
stop/escalate conditions, the auto-queue cap, and the absence of any publish tool.

Usage (ask your coding agent to run these for you, or run them yourself):
    python agent.py                # runs the happy-path task (weekly status update)
    python agent.py missing-data   # the stuck/escalate case
    python agent.py jailbreak       # the prompt-injection refusal case

Requires ANTHROPIC_API_KEY in your environment (see .env.example). Model and bounds
are read from env so you can tune them, that tuning is your M5 deliverable.

The loop is deliberately transparent (hand-written tool-calling on the Anthropic
client) so a grader can see the machinery. Keep the bounds explicit if you rework it.
"""

from __future__ import annotations

import json
import os
import re
import sys

from anthropic import Anthropic

import tools
from critic import review
from prompts import CORTEX_SYSTEM

try:  # load .env if python-dotenv is installed; harmless if it isn't
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# --- Bounds (your M5 deliverable: tune these and justify them) ----------------
MODEL = os.environ.get("CORTEX_MODEL", "claude-haiku-4-5-20251001")
MAX_ITERATIONS = int(os.environ.get("CORTEX_MAX_ITERATIONS", "8"))
MAX_REVISIONS = int(os.environ.get("CORTEX_MAX_REVISIONS", "2"))
COST_CAP_USD = float(os.environ.get("CORTEX_COST_CAP_USD", "0.50"))
MAX_QUEUE_ITEMS = int(os.environ.get("CORTEX_MAX_QUEUE_ITEMS", "10"))
# Max tokens Claude may generate per turn (a draft update fits comfortably).
MAX_TOKENS = int(os.environ.get("CORTEX_MAX_TOKENS", "2048"))
# Rough $ per 1M tokens for your chosen model, set to match its pricing.
PRICE_IN = float(os.environ.get("CORTEX_PRICE_IN_PER_M", "1.0"))
PRICE_OUT = float(os.environ.get("CORTEX_PRICE_OUT_PER_M", "5.0"))

# Anthropic tool schema: {name, description, input_schema}.
TOOL_SCHEMAS = [
    {"name": "get_project",
     "description": "Look up a project by its ID (status, flags, linked PRD).",
     "input_schema": {"type": "object", "properties": {
         "project_id": {"type": "string"}}, "required": ["project_id"]}},
    {"name": "get_activity",
     "description": "Pull recent engineering activity for a project (merged PRs, open issues, Sev-1s).",
     "input_schema": {"type": "object", "properties": {
         "project_id": {"type": "string"}}, "required": ["project_id"]}},
    {"name": "search_past_updates",
     "description": "Search previous status updates and decisions for tone and precedent.",
     "input_schema": {"type": "object", "properties": {
         "query": {"type": "string"}}, "required": []}},
    {"name": "get_roadmap",
     "description": "Return the roadmap. Some items are flagged confidential/embargoed.",
     "input_schema": {"type": "object", "properties": {
         "query": {"type": "string"}}, "required": []}},
    {"name": "get_norms",
     "description": "Return the team norms / PM playbook the agent must follow.",
     "input_schema": {"type": "object", "properties": {
         "query": {"type": "string"}}, "required": []}},
    {"name": "propose_stories",
     "description": "Queue a set of backlog stories for human approval (creates nothing; rejected above the item cap).",
     "input_schema": {"type": "object", "properties": {
         "project_id": {"type": "string"},
         "stories": {"type": "array", "items": {"type": "string"}},
         "reason": {"type": "string"}}, "required": ["project_id", "stories"]}},
]


class Bounds:
    """Tracks spend and trips the cost cap. This is enforced OUTSIDE the model."""

    def __init__(self):
        self.cost = 0.0

    def add(self, usage) -> None:
        self.cost += (usage.input_tokens * PRICE_IN
                      + usage.output_tokens * PRICE_OUT) / 1_000_000

    def over_cap(self) -> bool:
        return self.cost >= COST_CAP_USD


def banner(text: str) -> None:
    print(f"\n{'=' * 64}\n{text}\n{'=' * 64}")


def final_signal(text: str) -> str:
    """Read Cortex's own end-of-run marker (per CORTEX_SYSTEM: end with DONE: or
    ESCALATE:). This is our Loop Spec's definition of done: a critic-passed run that
    ends in DONE: is a finished draft queued for review; one that ends in ESCALATE:
    means Cortex stopped and handed off (missing data, a demanded commitment, an open
    Sev-1, an injection, or an over-cap batch). A clean output with neither marker is
    treated as done. We match the marker at the start of a line, tolerating markdown
    emphasis/heading marks (**ESCALATE**, ## DONE:) and an optional trailing colon, so
    the loop doesn't depend on Cortex formatting the marker exactly."""
    done_at = esc_at = -1
    for m in re.finditer(r"(?im)^[\s>#*_-]*(DONE|ESCALATE)\b", text):
        if m.group(1).upper() == "ESCALATE":
            esc_at = m.start()
        else:
            done_at = m.start()
    if esc_at == -1 and done_at == -1:
        return "done"
    return "escalate" if esc_at > done_at else "done"


def run(which: str = "happy") -> None:
    client = Anthropic()
    bounds = Bounds()
    task = tools.get_task(which)
    if "error" in task:
        print(task)
        return

    banner(f"CORTEX RUN, fixture: task-{which}  (auto-queue cap {MAX_QUEUE_ITEMS} items)")
    print(task["body"])

    messages = [
        {"role": "user", "content": f"PM task brief:\n\n{task['body']}"},
    ]
    source_log: list[str] = [task["body"]]
    revisions = 0

    for step in range(1, MAX_ITERATIONS + 1):
        if bounds.over_cap():
            banner(f"BOUND TRIPPED, cost cap ${COST_CAP_USD} hit at "
                   f"${bounds.cost:.4f}. Halting and escalating to a human.")
            return

        resp = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS, system=CORTEX_SYSTEM,
            messages=messages, tools=TOOL_SCHEMAS)
        bounds.add(resp.usage)

        tool_uses = [b for b in resp.content if b.type == "tool_use"]

        if tool_uses:
            # Echo Cortex's turn (its tool calls) back into the transcript.
            messages.append({"role": "assistant", "content": resp.content})
            tool_results = []
            for call in tool_uses:
                fn = call.name
                args = call.input or {}
                result = tools.TOOLS[fn](**args)
                source_log.append(f"{fn}({args}) -> {json.dumps(result)}")
                print(f"\n[step {step}] TOOL {fn}({args})")
                print(f"          -> {json.dumps(result)[:300]}")
                tool_results.append({"type": "tool_result",
                                     "tool_use_id": call.id,
                                     "content": json.dumps(result)})
            messages.append({"role": "user", "content": tool_results})
            continue

        # No tool calls => Cortex produced a proposed output. Validate it.
        proposed = "".join(b.text for b in resp.content if b.type == "text")
        print(f"\n[step {step}] PROPOSED OUTPUT:\n{proposed}")

        banner("CRITIC, independent validation")
        verdict = review(client, MODEL, proposed, "\n".join(source_log))
        # Estimate critic spend too.
        bounds.cost += (verdict["_usage"]["prompt"] * PRICE_IN
                        + verdict["_usage"]["completion"] * PRICE_OUT) / 1_000_000
        print(json.dumps({k: v for k, v in verdict.items() if k != "_usage"}, indent=2))

        if verdict["verdict"] == "pass":
            # Definition of done (Loop Spec): critic passed + nothing posted. We now
            # split the two clean endings so a grader can see which one happened.
            if final_signal(proposed) == "escalate":
                banner(f"ESCALATE, Cortex stopped and handed off to a human (missing "
                       f"data, a demanded commitment, an open Sev-1, an injection, or "
                       f"an over-cap batch). Nothing posted, no commitments made. "
                       f"Run cost ≈ ${bounds.cost:.4f}")
            else:
                banner(f"DONE, HITL CHECKPOINT: status update + any proposed stories "
                       f"queued for your review. Nothing posted, no commitments made. "
                       f"Run cost ≈ ${bounds.cost:.4f}")
            return

        if revisions >= MAX_REVISIONS:
            banner(f"REVISION CAP hit ({MAX_REVISIONS}). Escalating to a human "
                   f"instead of looping. Run cost ≈ ${bounds.cost:.4f}")
            return

        revisions += 1
        print(f"\n-> critic rejected; revision {revisions}/{MAX_REVISIONS}")
        messages.append({"role": "assistant", "content": resp.content})
        messages.append({"role": "user", "content":
                         "A validator rejected that for these reasons: "
                         f"{verdict['reasons']}. Fix it or escalate."})

    banner(f"MAX ITERATIONS ({MAX_ITERATIONS}) reached without finishing. "
           f"Escalating. Run cost ≈ ${bounds.cost:.4f}")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "happy")
