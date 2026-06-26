import sqlite3, subprocess, shutil, sys
from typing import Optional

FTS_QUERY_CHARS = '!"@#$%^&*()+={}[]:;<>,.?/~`'

def _snippet_from_row(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["tags"] = [t.strip() for t in d["tags"].split(",") if t.strip()] if d["tags"] else []
    d["favorite"] = bool(d["favorite"])
    return d

def _fts_escape(term: str) -> str:
    cleaned = ''.join(ch if ch not in FTS_QUERY_CHARS else ' ' for ch in term)
    tokens = cleaned.split()
    if not tokens:
        return ''
    return ' OR '.join(f'"{t}"*' for t in tokens)

def copy_to_clipboard(code: str) -> bool:
    try:
        import pyperclip; pyperclip.copy(code); return True
    except ImportError:
        system = sys.platform
        if system.startswith("linux"):
            if shutil.which("xclip"):
                proc = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
                proc.communicate(input=code.encode()); return proc.returncode == 0
            elif shutil.which("xsel"):
                proc = subprocess.Popen(["xsel", "-b"], stdin=subprocess.PIPE)
                proc.communicate(input=code.encode()); return proc.returncode == 0
            else:
                print("⚠️  Install xclip/xsel or `pip install pyperclip`"); return False
        elif system == "darwin":
            with subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE) as proc:
                proc.communicate(input=code.encode()); return proc.returncode == 0
        elif system == "win32":
            with subprocess.Popen(["clip"], stdin=subprocess.PIPE, shell=True) as proc:
                proc.communicate(input=code.encode()); return proc.returncode == 0
        else: print(f"⚠️  Unsupported: {system}"); return False