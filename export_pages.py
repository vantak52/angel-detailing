"""Export the static site for the GitHub Pages repository subpath."""
from pathlib import Path
import argparse
import re
import shutil

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--base-path', default='/angel-detailing')
args = parser.parse_args()
base = '/' + args.base_path.strip('/') if args.base_path.strip('/') else ''
if not re.fullmatch(r'(?:/[A-Za-z0-9._-]+)*', base):
    raise SystemExit('Use a URL path, for example /angel-detailing')
source = ROOT / 'dist'
destination = ROOT / 'docs'
if destination.resolve().parent != ROOT or destination.name != 'docs':
    raise SystemExit('Output must remain in this project’s docs directory')
if destination.exists():
    shutil.rmtree(destination)
destination.mkdir()
root_url = re.compile(r'''(["'])/(?!/)''')
for path in source.rglob('*'):
    if not path.is_file():
        continue
    out = destination / path.relative_to(source)
    out.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix in {'.html', '.css', '.js'}:
        text = path.read_text(encoding='utf-8')
        text = root_url.sub(lambda m: m[1] + base + '/', text)
        out.write_text(text, encoding='utf-8')
    else:
        shutil.copyfile(path, out)
(destination / '.nojekyll').write_text('', encoding='utf-8')
print(f'Exported {len(list(destination.rglob("*")))} entries for {base or "/"}')
