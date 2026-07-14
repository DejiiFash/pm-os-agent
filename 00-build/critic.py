"""Independent validator (M3). A separate model call that never saw the drafting
context, so it can't inherit the draft's blind spots. Returns a pass/fail verdict.
The revision cap that stops a critic<->drafter loop lives in `agent.py`.
"""

from __future__ import annotations

import json

from prompts import CRITIC_SYSTEM


def review(client, model: str, proposed_output: str, source_data: str) -> dict:
    """Return {"verdict": "pass"|"fail", "reasons": [...]} for a proposed output."""
    resp = client.messages.create(
        model=model,
        max_tokens=1024,
        system=CRITIC_SYSTEM,
        messages=[
            {"role": "user", "content":
                f"SOURCE DATA Cortex used:\n{source_data}\n\n"
                f"CORTEX PROPOSED OUTPUT:\n{proposed_output}"},
            # Prefill the reply with "{" so Claude must emit a JSON object.
            {"role": "assistant", "content": "{"},
        ],
    )
    usage = resp.usage
    text = "".join(b.text for b in resp.content if b.type == "text")
    try:
        verdict = json.loads("{" + text)
    except (json.JSONDecodeError, TypeError):
        verdict = {"verdict": "fail", "reasons": ["critic returned unparseable output"]}
    verdict["_usage"] = {"prompt": usage.input_tokens, "completion": usage.output_tokens}
    return verdict
