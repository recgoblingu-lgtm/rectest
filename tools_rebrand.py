from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parent
BASE = "/rectest/"
ICON = BASE + "logos/dreamrec/DreamRec%20icon.png"
THEME = BASE + "dreamrec-theme.css"

# Site-level copy and metadata only. User-generated titles, room names, and profile names remain untouched.
REPLACEMENTS = (
    ("recroom.network", "DreamRec"),
    ("Rec Room is the best place to build and play games together.", "DreamRec is a community hub for discovering rooms, creators, events, and profiles."),
    ("Purchase subscriptions or tokens for Rec Room.", "Explore DreamRec subscriptions and community features."),
    ("Rooms in Rec Room", "Rooms in DreamRec"),
    ("Creator Hub", "DreamRec Creator Hub"),
    ("Rec Room Shop", "DreamRec Shop"),
    ("Rec Room", "DreamRec"),
    ("#FF6727", "#16b7b0"),
    ("#FF5C00", "#0b7180"),
)


def add_brand_shell(text: str) -> str:
    if "data-dreamrec-brand" in text:
        return text
    marker = '<body>'
    if marker not in text:
        return text
    brand = (
        f'<div data-dreamrec-brand class="dreamrec-brand" role="banner">'
        f'<a href="{BASE}" aria-label="DreamRec home">'
        f'<img src="{ICON}" alt="DreamRec icon" width="42" height="42">'
        f'<span>DreamRec</span></a></div>'
    )
    return text.replace(marker, marker + brand, 1)


def process_html(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    # Use the local DreamRec mark for site-level Open Graph/Twitter images, not room/profile artwork.
    text = re.sub(r'(content=["\'])https://cdn\.recroom\.network/static/logos/[^"\']+', r'\1' + ICON, text)
    text = re.sub(r'(content=["\'])/logo\.png', r'\1' + ICON, text)
    text = text.replace(f'href="{THEME}"', f'href="{THEME}"')
    text = add_brand_shell(text)
    if text != original:
        path.write_text(text, encoding="utf-8")


def route_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return BASE
    if rel.endswith("/index.html"):
        return BASE + rel[:-len("index.html")]
    return BASE + rel


def make_link_directory() -> None:
    pages = sorted(
        p for p in ROOT.rglob("*.html")
        if ".git" not in p.parts and "tools_rebrand.py" not in p.name
        and p.name not in {"dreamrec-links.html"}
    )
    entries = []
    for p in pages:
        route = route_for(p)
        label = route.removeprefix(BASE).strip("/") or "home"
        entries.append(f'<li><a href="{escape(route)}">{escape(label)}</a></li>')
    body = "\n".join(entries)
    doc = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DreamRec Links</title>
<meta name="description" content="Browse every locally mirrored DreamRec HTML route.">
<link rel="icon" href="{BASE}favicon.ico"><link rel="stylesheet" href="{THEME}">
<style>
body{{margin:0;font-family:system-ui,sans-serif;background:#061a2a;color:#e6fbf8}}
.dreamrec-directory{{max-width:1100px;margin:0 auto;padding:1rem 1rem 4rem}}
.dreamrec-directory h1{{margin-top:2rem;color:#67eee0}}
.dreamrec-directory p{{color:#9bc8ca}}
.dreamrec-directory ul{{columns:3 280px;column-gap:2rem;padding:0;list-style:none}}
.dreamrec-directory li{{break-inside:avoid;margin:.35rem 0}}
.dreamrec-directory a{{color:#67eee0;text-decoration:none}}
.dreamrec-directory a:hover{{text-decoration:underline}}
</style></head><body>
<div class="dreamrec-brand" data-dreamrec-brand role="banner"><a href="{BASE}"><img src="{ICON}" alt="DreamRec icon" width="42" height="42"><span>DreamRec</span></a></div>
<main class="dreamrec-directory"><h1>DreamRec links</h1><p>{len(pages)} locally mirrored HTML pages and directory routes.</p><ul>{body}</ul></main>
</body></html>\n'''
    (ROOT / "dreamrec-links.html").write_text(doc, encoding="utf-8")
    (ROOT / "dreamrec-links").mkdir(exist_ok=True)
    (ROOT / "dreamrec-links" / "index.html").write_text(doc.replace('href="/rectest/dreamrec-links.html"', 'href="/rectest/dreamrec-links/"'), encoding="utf-8")


for html in ROOT.rglob("*.html"):
    if ".git" not in html.parts and html.name not in {"dreamrec-links.html"}:
        process_html(html)
make_link_directory()
print(f"Processed HTML pages and generated link directory from {len(list(ROOT.rglob('*.html')))} files.")
атtributes = None
THOOK = None
