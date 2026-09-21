from pathlib import Path
from urllib.parse import urlparse
from html.parser import HTMLParser
import re
import subprocess

ROOT = Path(__file__).resolve().parent
BASE_URL = "https://recroom.network"
BASE_PATH = "/rectest"
SITEMAP = Path('/home/ubuntu/recroom-sitemap.xml')

class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {'href', 'src'} and value:
                if value.startswith('/_next/') or value.startswith('/cdn-cgi/') or value.startswith('/logos/'):
                    self.urls.add(value.split('?', 1)[0])

def local_path(route: str) -> Path:
    route = route.strip('/')
    if not route:
        return ROOT / 'index.html'
    return ROOT / route / 'index.html'

def route_exists(route: str) -> bool:
    p = local_path(route)
    return p.exists() or (ROOT / (route.strip('/') + '.html')).exists()

def download(url: str) -> bytes:
    return subprocess.check_output(['curl', '-L', '-sS', '--max-time', '45', url])

def rewrite(text: str) -> str:
    text = text.replace('href="/', f'href="{BASE_PATH}/')
    text = text.replace('src="/', f'src="{BASE_PATH}/')
    text = text.replace("url(/", f"url({BASE_PATH}/")
    text = text.replace('https://recroom.network/', f'{BASE_PATH}/')
    text = text.replace('recroom.network', 'DreamRec')
    text = text.replace('Rec Room', 'DreamRec')
    text = text.replace('#FF6727', '#16b7b0').replace('#FF5C00', '#0b7180')
    if 'dreamrec-theme.css' not in text and '</head>' in text:
        text = text.replace('</head>', f'<link rel="stylesheet" href="{BASE_PATH}/dreamrec-theme.css"></head>', 1)
    if 'data-dreamrec-brand' not in text and '<body>' in text:
        brand = f'<div data-dreamrec-brand class="dreamrec-brand"><a href="{BASE_PATH}/"><img src="{BASE_PATH}/logos/dreamrec/DreamRec%20icon.png" alt="DreamRec icon" width="42" height="42"><span>DreamRec</span></a></div>'
        text = text.replace('<body>', '<body>' + brand, 1)
    return text

def main():
    xml = SITEMAP.read_text(errors='ignore')
    routes = [u.split(BASE_URL, 1)[1] for u in re.findall(r'<loc>([^<]+)</loc>', xml)]
    added = 0
    skipped = 0
    for route in routes:
        if route_exists(route):
            skipped += 1
            continue
        page = download(BASE_URL + route).decode('utf-8', errors='ignore')
        target = local_path(route)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rewrite(page), encoding='utf-8')
        parser = AssetParser(); parser.feed(page)
        for asset in parser.urls:
            target_asset = ROOT / asset.lstrip('/')
            if not target_asset.exists():
                target_asset.parent.mkdir(parents=True, exist_ok=True)
                try:
                    target_asset.write_bytes(download(BASE_URL + asset))
                except subprocess.CalledProcessError:
                    pass
        added += 1
    print(f'Added {added} sitemap routes; retained {skipped} existing routes.')

if __name__ == '__main__':
    main()
