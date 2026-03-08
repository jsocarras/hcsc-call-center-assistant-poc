# Call Center Assistant PoC (Payer / HCSC-like)

PoC-only Streamlit app that demonstrates the 6 requested use cases with dummy data and lightweight retrieval.

## What it includes
- Eligibility/benefits explainer (structured SoR-like dummy data → plain-language explanation)
- Claims status updates + denial/payment code translation
- Document search assistant over a small local corpus (simple lexical/fuzzy retrieval + citations)
- Transcript summarization + CRM logging (dummy CRM store)
- Prior auth status + next steps / missing info
- Monitoring checks (accuracy/tone/compliance heuristics + flags)

## Run
1. Create a virtual environment and install dependencies:
   - `python -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. Start the app:
   - `streamlit run app.py`

## Notes
- No external LLM calls are made. A small deterministic “LLM-like” summarizer is used so the PoC runs offline.
- Swap in a real on-prem/private LLM by implementing `llm.generate()` in `src/llm.py`.
