from __future__ import annotations

import re


def summarize_transcript(text: str) -> str:
    # Offline PoC summarizer: pull a few likely entities and create a SOAP-like note.
    text_clean = re.sub(r"\s+", " ", text).strip()

    concerns = []
    for kw in ["eligibility", "benefit", "claim", "denial", "prior authorization", "deductible", "copay", "appeal"]:
        if kw in text_clean.lower():
            concerns.append(kw)

    concerns = sorted(set(concerns))

    note = (
        "SOAP Note (PoC)\n"
        "S: Member called with questions regarding: "
        + (", ".join(concerns) if concerns else "general coverage")
        + ".\n"
        "O: Agent reviewed available plan and claim information in the tool.\n"
        "A: Explained current status in plain language; provided next-step guidance.\n"
        "P: Member advised of expected timelines and where to find supporting documents.\n\n"
        f"[Source: call transcript characters={len(text_clean)}]"
    )

    return note
