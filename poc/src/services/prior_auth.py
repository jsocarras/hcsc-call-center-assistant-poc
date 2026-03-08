from __future__ import annotations


def explain_prior_auth(pa: dict) -> dict:
    status = pa.get("status", "Unknown")
    decision = pa.get("decision", "Unknown")
    missing = pa.get("missing_items", [])

    citations = {
        "pa_fields": ["pa_id", "status", "decision", "service", "submitted_at", "updated_at", "missing_items"],
        "source": "dummy prior auth platform payload",
    }

    answer = (
        f"### Prior authorization summary\n\n"
        f"- **PA**: {pa.get('pa_id')}\n"
        f"- **Service**: {pa.get('service')}\n"
        f"- **Status**: **{status}**\n"
        f"- **Decision**: **{decision}**\n"
        f"- **Submitted**: {pa.get('submitted_at')}\n"
        f"- **Last updated**: {pa.get('updated_at')}\n\n"
    )

    if missing:
        answer += "### Missing information / next steps\n\n"
        answer += "To move this request forward, the following items are needed:\n"
        answer += "\n".join([f"- {m}" for m in missing]) + "\n\n"
        answer += "Once received, re-submit or attach to the existing request per workflow.\n"
    else:
        answer += (
            "### Next steps\n\n"
            "No missing items are listed in the current status. If the provider disagrees with the decision, "
            "review appeal rights and applicable timeframes.\n"
        )

    answer += f"\n[Source: dummy PA fields: {', '.join(citations['pa_fields'])}]\n"

    return {"answer": answer, "citations": citations}
