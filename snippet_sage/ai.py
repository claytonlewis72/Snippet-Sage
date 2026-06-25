from .database import get_snippet, get_statistics, _load_snippets

def ai_explain(code: str, language: str) -> str:
    return _mock_ai_explain(code, language)

def _mock_ai_explain(code, language):
    lines = code.strip().split("\n")
    return (f"This {language} snippet has {len(lines)} line(s). "
            "Consider adding a description for more context.")

def ai_find_related(snippet_id, top_n=3):
    target = get_snippet(snippet_id)
    if not target: return []
    all_s = _load_snippets()
    target_tags = set(target["tags"])
    scored = []
    for s in all_s:
        if s["id"] == snippet_id: continue
        overlap = len(target_tags & set(s["tags"]))
        if overlap > 0: scored.append((overlap, s))
    scored.sort(key=lambda x: -x[0])
    return [s for _, s in scored[:top_n]]