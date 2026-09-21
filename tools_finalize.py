from pathlib import Path

ROOT = Path(__file__).resolve().parent
LINK = '/rectest/dreamrec-links.html'

for path in ROOT.rglob('*.html'):
    if '.git' in path.parts or path.name == 'dreamrec-links.html':
        continue
    text = path.read_text(encoding='utf-8', errors='ignore')
    if 'data-dreamrec-brand' in text and 'dreamrec-directory-link' not in text:
        text = text.replace('</span></a></div>', f'</span></a><a class="dreamrec-directory-link" href="{LINK}">All links</a></div>', 1)
        path.write_text(text, encoding='utf-8')

for path in (ROOT / 'dreamrec-links.html', ROOT / 'dreamrec-links' / 'index.html'):
    text = path.read_text(encoding='utf-8', errors='ignore')
    if 'dreamrec-directory-link' not in text:
        text = text.replace('</span></a></div>', f'</span></a><a class="dreamrec-directory-link" href="{LINK}">All links</a></div>', 1)
        path.write_text(text, encoding='utf-8')

md = ROOT / 'dreamrec-links.md'
extra = '\n## Complete generated directory\n\n- https://recgoblingu-lgtm.github.io/rectest/dreamrec-links.html\n- https://recgoblingu-lgtm.github.io/rectest/dreamrec-links/\n'
if 'Complete generated directory' not in md.read_text(encoding='utf-8'):
    md.write_text(md.read_text(encoding='utf-8').rstrip() + extra, encoding='utf-8')

txt = ROOT / 'dreamrec-links.txt'
if 'dreamrec-links.html' not in txt.read_text(encoding='utf-8'):
    txt.write_text(txt.read_text(encoding='utf-8').rstrip() + '\nhttps://recgoblingu-lgtm.github.io/rectest/dreamrec-links.html\nhttps://recgoblingu-lgtm.github.io/rectest/dreamrec-links/\n', encoding='utf-8')
print('Finalized navigation and route manifests.')
