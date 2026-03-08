from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from src.monitoring import run_output_checks
from src.poc_data import (
    load_claims,
    load_docs,
    load_member,
    load_pa,
    load_transcripts,
)
from src.services.claims import explain_claim
from src.services.crm import CRMStore
from src.services.docs_search import search_docs
from src.services.eligibility import explain_eligibility_and_benefits
from src.services.prior_auth import explain_prior_auth
from src.services.transcripts import summarize_transcript

APP_DIR = Path(__file__).parent

st.set_page_config(page_title="Call Center Assistant PoC", layout="wide")

st.title("Call Center Assistant PoC (HCSC-like payer)")
st.caption(
    "PoC demonstrating eligibility/benefits, claims, doc search, transcript summarization + CRM notes, prior auth, and monitoring."
)

with st.sidebar:
    st.header("Context")
    member_id = st.text_input("Member ID", value="M0001")
    agent_id = st.text_input("Agent ID", value="A123")
    lob = st.selectbox("Line of Business (LoB)", ["Commercial", "Medicare", "Medicaid"], index=0)
    state = st.selectbox("State", ["IL", "TX", "NM", "OK", "MT"], index=0)

    st.divider()
    st.subheader("Mode")
    mode = st.radio(
        "Select use case",
        [
            "1) Eligibility & Benefits",
            "2) Claims Status",
            "3) Policy/Workflow Doc Search",
            "4) Transcript Summary + CRM Log",
            "5) Prior Authorization",
            "6) Monitoring Console",
        ],
        index=0,
    )

crm = CRMStore(db_path=APP_DIR / "data" / "crm_store.json")

member = load_member(member_id)
claims = load_claims(member_id)
pa_list = load_pa(member_id)
docs = load_docs()
transcripts = load_transcripts(member_id)

# --- Header summary
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Member", member.get("name", "Unknown"))
with c2:
    st.metric("Member ID", member_id)
with c3:
    st.metric("LoB", lob)
with c4:
    st.metric("State", state)

st.divider()

# --- Use cases
if mode.startswith("1"):
    st.subheader("1) Eligibility & Benefits Explainer")
    st.write("Structured SoR-like data → plain-language explanation + citations.")

    if not member:
        st.error("Member not found in dummy dataset.")
    else:
        explanation = explain_eligibility_and_benefits(member)
        st.markdown(explanation["answer"])
        with st.expander("Citations / Source fields"):
            st.json(explanation["citations"])

        checks = run_output_checks(explanation["answer"], context={"member_id": member_id, "lob": lob, "state": state})
        with st.expander("Monitoring checks"):
            st.json(checks)

elif mode.startswith("2"):
    st.subheader("2) Claims status + code translation")
    st.write("Dummy claims feed → human-readable claim status, code translation, and next steps.")

    if not claims:
        st.info("No claims found for this member in dummy dataset.")
    else:
        claim_ids = [c["claim_id"] for c in claims]
        selected = st.selectbox("Select claim", claim_ids)
        claim = next(c for c in claims if c["claim_id"] == selected)

        explained = explain_claim(claim)
        st.markdown(explained["answer"])

        colA, colB = st.columns(2)
        with colA:
            st.caption("Raw claim")
            st.json(claim)
        with colB:
            st.caption("Citations")
            st.json(explained["citations"])

        checks = run_output_checks(explained["answer"], context={"member_id": member_id})
        with st.expander("Monitoring checks"):
            st.json(checks)

elif mode.startswith("3"):
    st.subheader("3) Search assistant (policy/benefit/workflow docs)")
    st.write("Local doc corpus → retrieval + summary + citations (PoC retrieval uses fuzzy + keyword scoring).")

    q = st.text_input("Question / search query", value="Does prior auth require clinical notes for MRI?")
    top_k = st.slider("Top K", min_value=1, max_value=5, value=3)

    if st.button("Search", type="primary"):
        results = search_docs(docs, query=q, top_k=top_k)
        if not results:
            st.warning("No results found.")
        else:
            st.markdown("### Answer (PoC)")
            # Very simple answer composer for PoC.
            bullets = "\n".join([f"- **{r['title']}**: {r['snippet']}" for r in results])
            answer = (
                f"Here are the most relevant internal references I found for: **{q}**\n\n"
                f"{bullets}\n\n"
                "If you need an exact procedure, open the linked doc and follow the numbered workflow steps."
            )
            st.markdown(answer)

            st.markdown("### Citations")
            st.json([{k: r[k] for k in ("doc_id", "title", "url", "score")} for r in results])

            checks = run_output_checks(answer, context={"query": q})
            with st.expander("Monitoring checks"):
                st.json(checks)

elif mode.startswith("4"):
    st.subheader("4) Transcript summarization + automatic CRM notes")
    st.write("Dummy transcript → structured summary → create CRM case note (agent reviews before saving).")

    if not transcripts:
        st.info("No transcripts available for this member in dummy dataset.")
    else:
        t_ids = [t["transcript_id"] for t in transcripts]
        tid = st.selectbox("Select transcript", t_ids)
        transcript = next(t for t in transcripts if t["transcript_id"] == tid)

        st.caption("Transcript")
        st.text_area("", value=transcript["text"], height=200)

        if st.button("Generate summary", type="primary"):
            summary = summarize_transcript(transcript["text"])
            st.session_state["draft_note"] = summary

        draft = st.session_state.get("draft_note")
        if draft:
            st.markdown("### Draft (agent review)")
            edited = st.text_area("Edit note before logging to CRM", value=draft, height=220)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Log to CRM", type="primary"):
                    case = crm.create_case(
                        member_id=member_id,
                        agent_id=agent_id,
                        subject=f"Call summary for {member_id}",
                        note=edited,
                        metadata={"transcript_id": tid, "created_at": datetime.utcnow().isoformat()},
                    )
                    st.success(f"Logged note to CRM case {case['case_id']}")
            with col2:
                if st.button("Discard"):
                    st.session_state.pop("draft_note", None)

            checks = run_output_checks(edited, context={"member_id": member_id, "transcript_id": tid})
            with st.expander("Monitoring checks"):
                st.json(checks)

    st.markdown("### CRM cases")
    st.json(crm.list_cases(member_id=member_id))

elif mode.startswith("5"):
    st.subheader("5) Prior authorization status + next steps")
    st.write("Dummy PA requests → status, determination reason, missing items, and next steps.")

    if not pa_list:
        st.info("No prior authorizations found for this member in dummy dataset.")
    else:
        pa_ids = [p["pa_id"] for p in pa_list]
        selected = st.selectbox("Select PA", pa_ids)
        pa = next(p for p in pa_list if p["pa_id"] == selected)

        explained = explain_prior_auth(pa)
        st.markdown(explained["answer"])

        colA, colB = st.columns(2)
        with colA:
            st.caption("Raw PA")
            st.json(pa)
        with colB:
            st.caption("Citations")
            st.json(explained["citations"])

        checks = run_output_checks(explained["answer"], context={"member_id": member_id, "pa_id": selected})
        with st.expander("Monitoring checks"):
            st.json(checks)

elif mode.startswith("6"):
    st.subheader("6) Monitoring console (PoC)")
    st.write(
        "This PoC implements lightweight checks (tone, PHI leakage patterns, missing citations). In production this would be event-driven with dashboards and QA sampling."
    )

    sample_text = st.text_area(
        "Paste any assistant output to check",
        value="Your member John Doe has HIV and owes $1,234. Call us at 555-123-4567.",
        height=180,
    )
    checks = run_output_checks(sample_text, context={"member_id": member_id})
    st.json(checks)

    st.markdown("### Current CRM store (for demo traceability)")
    st.code(json.dumps(crm.dump(), indent=2))
