from __future__ import annotations


def explain_eligibility_and_benefits(member: dict) -> dict:
    coverage = member.get("coverage", {})
    benefits = member.get("benefits", {})

    # Deterministic-first: compute a few derived values.
    in_network = benefits.get("in_network", {})
    ded = in_network.get("deductible", {})

    citations = {
        "member_fields": ["member_id", "coverage.status", "coverage.effective_date", "coverage.termination_date"],
        "benefit_fields": [
            "benefits.in_network.deductible",
            "benefits.in_network.oop_max",
            "benefits.in_network.primary_care_visit",
            "benefits.in_network.specialist_visit",
            "benefits.in_network.rx_tier_1",
        ],
        "source": "dummy SoR payload",
    }

    answer = (
        f"### Eligibility summary\n\n"
        f"- **Coverage status**: **{coverage.get('status', 'Unknown')}**\n"
        f"- **Effective date**: {coverage.get('effective_date', 'Unknown')}\n"
        f"- **Termination date**: {coverage.get('termination_date', 'N/A')}\n\n"
        f"### Key in-network benefits (plain language)\n\n"
        f"- **Deductible**: You pay **${ded.get('individual', 0):,.0f}** per year before the plan starts sharing costs for many services. "
        f"Your deductible already met this year is **${ded.get('met_to_date', 0):,.0f}**.\n"
        f"- **Out-of-pocket max**: Your yearly maximum you would pay for covered in-network services is "
        f"**${in_network.get('oop_max', {}).get('individual', 0):,.0f}**.\n"
        f"- **Primary care visit**: Typically **{in_network.get('primary_care_visit', 'See plan')}**.\n"
        f"- **Specialist visit**: Typically **{in_network.get('specialist_visit', 'See plan')}**.\n"
        f"- **Rx Tier 1**: Typically **{in_network.get('rx_tier_1', 'See plan')}**.\n\n"
        f"[Source: dummy SoR payload fields: {', '.join(citations['member_fields'] + citations['benefit_fields'])}]\n"
    )

    return {"answer": answer, "citations": citations}
