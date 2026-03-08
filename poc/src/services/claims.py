from __future__ import annotations

CARC = {
    "197": "Precertification/authorization/notification absent",
    "96": "Non-covered charge(s)",
}

RARC = {
    "N130": "Consult plan benefit documents to determine if service is covered",
    "N290": "Missing/invalid provider identifier",
}

PAYMENT_CODES = {
    "P": "Paid",
    "D": "Denied",
    "R": "Pending/Review",
}


def explain_claim(claim: dict) -> dict:
    status = claim.get("status", "Unknown")
    pay_code = claim.get("payment_code")
    carc = claim.get("carc")
    rarc = claim.get("rarc")

    status_plain = PAYMENT_CODES.get(pay_code, status)
    carc_plain = CARC.get(carc, "(unknown code)") if carc else None
    rarc_plain = RARC.get(rarc, "(unknown code)") if rarc else None

    next_steps = []
    if pay_code == "D":
        next_steps.append("Confirm whether prior authorization was required and obtained")
        next_steps.append("Check if an appeal is appropriate and within filing limits")
        next_steps.append("Verify provider identifiers and claim submission values")
    elif pay_code == "R":
        next_steps.append("Advise the caller the claim is under review and provide expected turnaround time")

    citations = {
        "claim_fields": ["claim_id", "status", "payment_code", "carc", "rarc", "amount_billed", "amount_paid"],
        "code_tables": ["CARC", "RARC", "PAYMENT_CODES"],
        "source": "dummy claims feed + local dictionaries",
    }

    answer = (
        f"### Claim status summary\n\n"
        f"- **Claim**: {claim.get('claim_id')}\n"
        f"- **Status**: **{status_plain}**\n"
        f"- **Amount billed**: ${claim.get('amount_billed', 0):,.2f}\n"
        f"- **Amount paid**: ${claim.get('amount_paid', 0):,.2f}\n\n"
    )

    if pay_code == "D":
        answer += "### Denial explanation (plain language)\n\n"
        if carc:
            answer += f"- **CARC {carc}**: {carc_plain}\n"
        if rarc:
            answer += f"- **RARC {rarc}**: {rarc_plain}\n"
        if next_steps:
            answer += "\n### Suggested next steps\n\n" + "\n".join([f"- {s}" for s in next_steps]) + "\n"
    elif pay_code == "P":
        answer += (
            "### Payment summary\n\n"
            "This claim has been processed and paid. If the member or provider disputes the amount, "
            "review the EOB and contractual adjustments.\n"
        )
    else:
        answer += (
            "### What this means\n\n"
            "This claim is not finalized yet. Provide the most recent timestamp and set expectations for next update.\n"
        )

    answer += f"\n[Source: dummy claim fields: {', '.join(citations['claim_fields'])}]\n"

    return {"answer": answer, "citations": citations}
