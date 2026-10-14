"""Build a static photo wall using repository photos and the shared visibility list."""
import json
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif'}

def make_manifest():
    catalog = json.loads((ROOT / 'data/catalog.json').read_text())
    files = sorted((ROOT / 'assets/photos').iterdir(), key=lambda path: path.name.casefold(), reverse=True)
    by_id = {}
    for path in files:
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        if not path.stat().st_size:
            raise ValueError(f'Empty image: {path.name}')
        if path.stem in by_id:
            raise ValueError(f'Photo filenames must have unique stems: {path.stem}')
        by_id[path.stem] = {'id': path.stem, 'filename': path.name,
                           'src': 'assets/photos/' + quote(path.name)}
    imported_ids = [photo['id'] for photo in catalog['photos']]
    missing = set(imported_ids) - by_id.keys()
    if missing:
        raise ValueError(f'Imported photos missing from assets/photos: {sorted(missing)[:5]}')
    new_ids = [photo_id for photo_id in by_id if photo_id not in set(imported_ids)]
    rows = [new_ids[index:index + 3] for index in range(0, len(new_ids), 3)] + catalog['rows']
    if set(photo_id for row in rows for photo_id in row) != set(by_id):
        raise ValueError('Row grouping and photo catalog do not match')
    for row in rows:
        if not 1 <= len(row) <= 3:
            raise ValueError('Each row must contain between one and three photos')
    return {'version': 1, 'photos': [by_id[photo_id] for photo_id in new_ids + imported_ids], 'rows': rows}

def build():
    visibility = json.loads((ROOT / 'data/visibility.json').read_text())
    if visibility.get('version') != 1 or not isinstance(visibility.get('hidden'), list):
        raise ValueError('visibility.json must contain version: 1 and a hidden array')
    if any(not isinstance(photo_id, str) or not photo_id.strip() for photo_id in visibility['hidden']):
        raise ValueError('Hidden IDs must be non-empty strings')
    manifest = make_manifest()
    if len(visibility['hidden']) != len(set(visibility['hidden'])):
        raise ValueError('Duplicate hidden IDs')
    output = ROOT / 'dist'
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    for filename in ['index.html', 'admin.html', 'style.css', 'admin.css', 'gallery.js', 'wall.js', 'admin.js']:
        shutil.copy2(ROOT / filename, output / filename)
    shutil.copytree(ROOT / 'assets/photos', output / 'assets/photos')
    (output / 'data').mkdir()
    (output / 'data/photos.json').write_text(json.dumps(manifest, ensure_ascii=False, separators=(',', ':')))
    shutil.copy2(ROOT / 'data/visibility.json', output / 'data/visibility.json')
    (output / '.nojekyll').touch()
    print(f'Built {len(manifest["photos"])} photos in {len(manifest["rows"])} rows; '
          f'{len(visibility["hidden"])} hidden IDs.')

if __name__ == '__main__':
    build()
