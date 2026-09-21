from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "profiles.txt"
MANIFEST = ROOT / "profile-sync-manifest.json"
RESULTS = ROOT / "profile-sync-results.md"
BASE = "/rectest"
ALLOWED_HOSTS = {"recroom.network", "www.recroom.network"}
USER_RE = re.compile(r"^/user/([^/]+)/?$")


def read_urls() -> list[str]:
    urls = []
    for line in QUEUE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line not in urls:
            urls.append(line)
    return urls


def profile_name(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        return None
    match = USER_RE.match(parsed.path)
    if not match or not match.group(1):
        return None
    return match.group(1)


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "DreamRec-approved-profile-sync/1.0"})
    with urlopen(req, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        return response.read().decode("utf-8", errors="replace")


def rewrite_html(html: str) -> str:
    html = html.replace('href="/', f'href="{BASE}/')
    html = html.replace('src="/', f'src="{BASE}/')
    html = html.replace("url(/", f"url({BASE}/")
    html = html.replace("recroom.network", "DreamRec")
    html = html.replace("img.DreamRec", "img.recroom.network")
    html = html.replace("cdn.DreamRec", "cdn.recroom.network")
    html = html.replace("static.DreamRec", "static.recroom.network")
    html = html.replace("Rec Room", "DreamRec")
    html = html.replace("#FF6727", "#16b7b0").replace("#FF5C00", "#0b7180")
    html = html.replace('/logo.png', '/logos/dreamrec/DreamRec%20icon.png')
    if "dreamrec-theme.css" not in html and "</head>" in html:
        html = html.replace("</head>", f'<link rel="stylesheet" href="{BASE}/dreamrec-theme.css"></head>', 1)
    if "data-dreamrec-brand" not in html and "<body>" in html:
        brand = (
            f'<div data-dreamrec-brand class="dreamrec-brand" role="banner">'
            f'<a href="{BASE}/" aria-label="DreamRec home">'
            f'<img src="{BASE}/logos/dreamrec/DreamRec%20icon.png" alt="DreamRec icon" width="42" height="42">'
            f'<span>DreamRec</span></a><a class="dreamrec-directory-link" href="{BASE}/dreamrec-links.html">All links</a></div>'
        )
        html = html.replace("<body>", "<body>" + brand, 1)
    return html


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"processed": {}, "updated_at": None}


def save_manifest(manifest: dict) -> None:
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_results(results: list[tuple[str, str, str]]) -> None:
    lines = ["# DreamRec profile sync results", "", f"Last run: {datetime.now(timezone.utc).isoformat()}", "", "| Profile | Status | Detail |", "|---|---|---|"]
    for url, status, detail in results:
        lines.append(f"| `{url}` | **{status}** | {detail.replace('|', '/')[:180]} |")
    RESULTS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()

    manifest = load_manifest()
    processed = manifest.setdefault("processed", {})
    results = []
    candidates = []
    for url in read_urls():
        name = profile_name(url)
        if not name:
            results.append((url, "SKIPPED", "Only https://recroom.network/user/<name>/ URLs are accepted"))
            continue
        if url in processed and processed[url].get("status") == "success":
            continue
        candidates.append((url, name))
        if len(candidates) >= args.limit:
            break

    for index, (url, name) in enumerate(candidates):
        target = ROOT / "user" / name / "index.html"
        try:
            html = fetch(url)
            if "404" in html[:5000] and "Page Not Found" in html[:5000]:
                raise RuntimeError("page appears to be a 404")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rewrite_html(html), encoding="utf-8")
            processed[url] = {"status": "success", "path": str(target.relative_to(ROOT)), "updated_at": datetime.now(timezone.utc).isoformat()}
            results.append((url, "OK", str(target.relative_to(ROOT))))
        except Exception as exc:
            processed[url] = {"status": "failed", "error": str(exc), "updated_at": datetime.now(timezone.utc).isoformat()}
            results.append((url, "FAILED", str(exc)))
        if index + 1 < len(candidates):
            time.sleep(max(0.0, args.delay))

    save_manifest(manifest)
    append_results(results or [("(none)", "OK", "No unprocessed approved URLs were available")])
    print(f"Processed {len(candidates)} approved profile URLs; {sum(1 for _, s, _ in results if s == 'OK')} succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
