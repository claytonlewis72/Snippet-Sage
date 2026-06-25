import argparse, sys
from .database import init_db, add_snippet, list_snippets, get_snippet_by_partial_id, delete_snippet, \
    toggle_favorite, edit_snippet, get_statistics, export_snippets, import_snippets
from .ai import ai_explain, ai_find_related
from .utils import copy_to_clipboard

def _format_snippet(s, verbose=False):
    fav = "⭐" if s.get("favorite") else ""
    parts = [
        f"\n{'═'*60}",
        f"  [{s['id']}] {s['title']} {fav}",
        f"  Language: {s['language']}  |  Tags: {', '.join(s['tags']) or '(none)'}",
        f"  Created:  {s['created'][:19]}",
    ]
    if verbose:
        parts.append(f"  Description: {s['description'] or '(none)'}")
        parts.append("  Code:")
        for line in s["code"].split("\n"): parts.append(f"    │ {line}")
    else:
        preview = s["code"][:120].replace("\n", "↵ ")
        parts.append(f"  Code: {preview}{'…' if len(s['code'])>120 else ''}")
    parts.append(f"{'═'*60}")
    return "\n".join(parts)

def main():
    init_db()
    parser = argparse.ArgumentParser(prog="snippet-sage", description="🧠 AI-Powered Code Snippet Manager")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("add"); p.add_argument("title"); p.add_argument("language"); p.add_argument("code")
    p.add_argument("-d","--description",default=""); p.add_argument("-t","--tags",default="")

    p = sub.add_parser("list"); p.add_argument("-l","--language",default="")
    p.add_argument("-t","--tag",default=""); p.add_argument("-s","--search",default="")
    p.add_argument("--id",default=""); p.add_argument("-v","--verbose",action="store_true")
    p.add_argument("--raw",action="store_true")

    for cmd in ["get","delete","favorite","copy","show","explain"]:
        p = sub.add_parser(cmd); p.add_argument("id")

    p = sub.add_parser("edit"); p.add_argument("id")
    p.add_argument("--title",default=""); p.add_argument("--language",default="")
    p.add_argument("--code",default=""); p.add_argument("--description",default="")
    p.add_argument("--tags",default="")

    sub.add_parser("stats")
    p = sub.add_parser("export"); p.add_argument("filepath")
    p = sub.add_parser("import"); p.add_argument("filepath"); p.add_argument("--merge",action="store_true")
    p = sub.add_parser("related"); p.add_argument("id"); p.add_argument("-n","--top-n",type=int,default=3)

    args = parser.parse_args()
    if not args.command: parser.print_help(); return

    def resolve(id_): return get_snippet_by_partial_id(id_)

    if args.command == "add":
        s = add_snippet(args.title, args.language, args.code, args.description,
                        [t.strip() for t in args.tags.split(",") if t.strip()])
        print(f"✅ Added [{s['id']}] — {s['title']}")
    elif args.command == "list":
        results = list_snippets(args.language, args.tag, args.search, args.id)
        if not results: print("📭 None found."); return
        if args.raw:
            for s in results:
                print(f"# [{s['id']}] {s['title']} ({s['language']})"); print(s["code"]); print()
        else:
            print(f"\n📚 {len(results)} snippet(s):")
            for s in results: print(_format_snippet(s, args.verbose))
    elif args.command == "get":
        s = resolve(args.id)
        print(_format_snippet(s, verbose=True) if s else f"❌ '{args.id}' not found.")
    elif args.command == "delete":
        s = resolve(args.id)
        if s and delete_snippet(s["id"]): print(f"🗑️ Deleted [{s['id']}] — {s['title']}")
        else: print(f"❌ Not found.")
    elif args.command == "edit":
        s = resolve(args.id)
        if not s: print(f"❌ Not found."); return
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None
        updated = edit_snippet(s["id"], args.title, args.language, args.code, args.description, tags)
        if updated: print(f"✏️ Updated [{updated['id']}] — {updated['title']}")
    elif args.command == "favorite":
        s = resolve(args.id)
        if not s: print(f"❌ Not found."); return
        toggled = toggle_favorite(s["id"])
        st = "⭐ favorited" if toggled["favorite"] else "☆ unfavorited"
        print(f"{st} [{toggled['id']}] {toggled['title']}")
    elif args.command == "copy":
        s = resolve(args.id)
        if not s: print(f"❌ Not found."); return
        if copy_to_clipboard(s["code"]): print(f"📋 Copied [{s['id']}] {s['title']}")
        else: print("❌ Clipboard failed.")
    elif args.command == "show":
        s = resolve(args.id)
        if s: print(f"# ── [{s['id']}] {s['title']} ({s['language']}) ──\n{s['code']}")
        else: print(f"❌ Not found.")
    elif args.command == "stats":
        st = get_statistics()
        print(f"\n📊 Statistics\n{'─'*40}\nTotal: {st['total']}   Favorites: {st['favorites']}")
        print("\nLanguages:"); [print(f"  {l}: {c}") for l,c in st['languages'].items()]
        if st['top_tags']: print("\nTop Tags:"); [print(f"  #{t}: {c}") for t,c in st['top_tags'].items()]
    elif args.command == "export": export_snippets(args.filepath)
    elif args.command == "import": import_snippets(args.filepath, args.merge)
    elif args.command == "explain":
        s = resolve(args.id)
        if s: print(f"\n🤖 {ai_explain(s['code'], s['language'])}")
        else: print(f"❌ Not found.")
    elif args.command == "related":
        s = resolve(args.id)
        if not s: print(f"❌ Not found."); return
        rel = ai_find_related(s["id"], args.top_n)
        if not rel: print("🔍 None found.")
        else:
            print(f"\n🔗 Related to [{s['id']}] {s['title']}:")
            for r in rel: print(f"  [{r['id']}] {r['title']} ({r['language']})  #{', '.join(r['tags'])}")
    else: parser.print_help()