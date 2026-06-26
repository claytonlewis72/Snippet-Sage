import sqlite3, uuid, json
from datetime import datetime
from pathlib import Path
from typing import Optional
from .utils import _snippet_from_row, _fts_escape

DATA_DIR = Path.home() / ".snippet_sage"
DATABASE_PATH = DATA_DIR / "snippets.db"

def _get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row; conn.execute("PRAGMA journal_mode=WAL"); return conn

def init_db():
    with _get_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS snippets (
            id TEXT PRIMARY KEY, title TEXT NOT NULL, language TEXT NOT NULL DEFAULT '',
            code TEXT NOT NULL, description TEXT DEFAULT '', tags TEXT DEFAULT '',
            created TEXT NOT NULL, updated TEXT NOT NULL, favorite INTEGER DEFAULT 0)""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_language ON snippets(language)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_favorite ON snippets(favorite)")
        conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS snippets_fts USING fts5(
            title, description, code, tags, content='snippets', content_rowid='rowid')""")
        conn.executescript("""
            CREATE TRIGGER IF NOT EXISTS snippets_ai AFTER INSERT ON snippets BEGIN
                INSERT INTO snippets_fts(rowid, title, description, code, tags)
                VALUES (new.rowid, new.title, new.description, new.code, new.tags); END;
            CREATE TRIGGER IF NOT EXISTS snippets_ad AFTER DELETE ON snippets BEGIN
                INSERT INTO snippets_fts(snippets_fts, rowid, title, description, code, tags)
                VALUES ('delete', old.rowid, old.title, old.description, old.code, old.tags); END;
            CREATE TRIGGER IF NOT EXISTS snippets_au AFTER UPDATE ON snippets BEGIN
                INSERT INTO snippets_fts(snippets_fts, rowid, title, description, code, tags)
                VALUES ('delete', old.rowid, old.title, old.description, old.code, old.tags);
                INSERT INTO snippets_fts(rowid, title, description, code, tags)
                VALUES (new.rowid, new.title, new.description, new.code, new.tags); END;""")
        conn.execute("INSERT INTO snippets_fts(snippets_fts) VALUES('rebuild')")

def _load_snippets():
    with _get_connection() as conn:
        rows = conn.execute("SELECT * FROM snippets ORDER BY created DESC").fetchall()
        return [_snippet_from_row(row) for row in rows]

def add_snippet(title, language, code, description="", tags=None):
    sid = str(uuid.uuid4())[:8]; now = datetime.now().isoformat()
    tags_str = ",".join([t.lower().strip() for t in (tags or [])])
    with _get_connection() as conn:
        conn.execute("""INSERT INTO snippets (id, title, language, code, description, tags, created, updated, favorite)
            VALUES (?,?,?,?,?,?,?,?,0)""", (sid, title, language.lower(), code, description, tags_str, now, now))
    return get_snippet(sid)

def list_snippets(language="", tag="", search="", snippet_id_prefix=""):
    q = ["SELECT s.* FROM snippets s"]; p = []
    if search:
        q.append("JOIN snippets_fts fts ON s.rowid = fts.rowid"); q.append("WHERE snippets_fts MATCH ?")
        fts_query = _fts_escape(search)
        if not fts_query:
            q.pop(); q.pop()
            w = ["1=1"]
            if language: w.append("s.language = ?"); p.append(language.lower())
            if tag: w.append("instr(','||s.tags||',',?)>0"); p.append(f",{tag.lower()},")
            q.append("WHERE " + " AND ".join(w))
        else:
            p.append(fts_query); fc = []
            if language: fc.append("s.language = ?"); p.append(language.lower())
            if tag: fc.append("instr(','||s.tags||',',?)>0"); p.append(f",{tag.lower()},")
            if fc: q.append("AND "+" AND ".join(fc))
    else:
        w = ["1=1"]
        if language: w.append("s.language = ?"); p.append(language.lower())
        if tag: w.append("instr(','||s.tags||',',?)>0"); p.append(f",{tag.lower()},")
        q.append("WHERE " + " AND ".join(w))
    if snippet_id_prefix: q.append("AND s.id LIKE ?"); p.append(snippet_id_prefix+"%")
    q.append("ORDER BY s.created DESC")
    with _get_connection() as conn:
        return [_snippet_from_row(r) for r in conn.execute(" ".join(q), p).fetchall()]

def get_snippet(snippet_id):
    with _get_connection() as conn:
        row = conn.execute("SELECT * FROM snippets WHERE id=?", (snippet_id,)).fetchone()
        return _snippet_from_row(row) if row else None

def get_snippet_by_partial_id(partial_id):
    s = get_snippet(partial_id)
    if s: return s
    with _get_connection() as conn:
        rows = conn.execute("SELECT * FROM snippets WHERE id LIKE ?||'%'", (partial_id,)).fetchall()
    if not rows: return None
    if len(rows)==1: return _snippet_from_row(rows[0])
    print(f"⚠️  Multiple matches for '{partial_id}':")
    for r in rows:
        s = _snippet_from_row(r); print(f"  [{s['id']}] {s['title']} ({s['language']})")
    return None

def delete_snippet(snippet_id):
    with _get_connection() as conn:
        cur = conn.execute("DELETE FROM snippets WHERE id=?", (snippet_id,))
        return cur.rowcount > 0

def toggle_favorite(snippet_id):
    with _get_connection() as conn:
        conn.execute("UPDATE snippets SET favorite=1-favorite, updated=? WHERE id=?",
                     (datetime.now().isoformat(), snippet_id))
        r = conn.execute("SELECT * FROM snippets WHERE id=?", (snippet_id,)).fetchone()
        return _snippet_from_row(r) if r else None

def edit_snippet(snippet_id, title="", language="", code="", description="", tags=None):
    up=[]; p=[]
    if title: up.append("title=?"); p.append(title)
    if language: up.append("language=?"); p.append(language.lower())
    if code: up.append("code=?"); p.append(code)
    if description: up.append("description=?"); p.append(description)
    if tags is not None: up.append("tags=?"); p.append(",".join(t.lower().strip() for t in tags))
    if not up: return get_snippet(snippet_id)
    up.append("updated=?"); p.append(datetime.now().isoformat()); p.append(snippet_id)
    with _get_connection() as conn:
        conn.execute(f"UPDATE snippets SET {', '.join(up)} WHERE id=?", p)
        r = conn.execute("SELECT * FROM snippets WHERE id=?", (snippet_id,)).fetchone()
        return _snippet_from_row(r) if r else None

def get_statistics():
    with _get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM snippets").fetchone()[0]
        fav = conn.execute("SELECT COUNT(*) FROM snippets WHERE favorite=1").fetchone()[0]
        langs = {r["language"]: r["cnt"] for r in conn.execute(
            "SELECT language, COUNT(*) cnt FROM snippets GROUP BY language ORDER BY cnt DESC")}
        tag_counts = {}
        for r in conn.execute("SELECT tags FROM snippets"):
            for t in r["tags"].split(","):
                t = t.strip()
                if t: tag_counts[t] = tag_counts.get(t, 0) + 1
        top = dict(sorted(tag_counts.items(), key=lambda x:-x[1])[:10])
        return {"total": total, "favorites": fav, "languages": langs, "top_tags": top}

def export_snippets(filepath):
    snippets = _load_snippets()
    with open(filepath, "w") as f: json.dump(snippets, f, indent=2)
    print(f"✅ Exported {len(snippets)} to {filepath}")

def import_snippets(filepath, merge=False):
    with open(filepath) as f: incoming = json.load(f)
    if not merge:
        with _get_connection() as conn: conn.execute("DELETE FROM snippets")
    for s in incoming:
        add_snippet(s["title"], s["language"], s["code"], s.get("description",""), s.get("tags",[]))
    print(f"✅ Imported {len(incoming)} snippets{' (merged)' if merge else ''}.")