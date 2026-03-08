from __future__ import annotations

# RapidFuzz is preferred, but keep PoC runnable even if the optional wheel
# isn't available for the current interpreter.
try:
    from rapidfuzz import fuzz  # type: ignore
except Exception:  # pragma: no cover
    import difflib

    class _FuzzFallback:
        @staticmethod
        def token_set_ratio(a: str, b: str) -> float:
            return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100.0

        @staticmethod
        def partial_ratio(a: str, b: str) -> float:
            # Simple approximation for PoC.
            return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100.0

    fuzz = _FuzzFallback()


def _score(query: str, text: str) -> float:
    # PoC: combine token_set_ratio with partial_ratio.
    return 0.6 * fuzz.token_set_ratio(query, text) + 0.4 * fuzz.partial_ratio(query, text)


def search_docs(docs: list[dict], query: str, top_k: int = 3) -> list[dict]:
    if not query.strip():
        return []

    scored = []
    for d in docs:
        hay = f"{d.get('title','')}\n{d.get('body','')}"
        s = _score(query, hay)
        scored.append((s, d))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for s, d in scored[:top_k]:
        body = d.get("body", "")
        snippet = body[:220].strip().replace("\n", " ")
        results.append(
            {
                "doc_id": d.get("doc_id"),
                "title": d.get("title"),
                "url": d.get("url"),
                "score": round(float(s), 2),
                "snippet": snippet + ("..." if len(body) > 220 else ""),
            }
        )

    return results
