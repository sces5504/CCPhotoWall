"""Build a static photo wall using repository photos and the shared visibility list."""
import json
import shutil
from pathlib import Path
from urllib.parse import quote, unquote
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif'}
THUMBNAIL_SIZE = 640

def index_images(directory):
    images = {}
    if not directory.is_dir():
        return images
    for path in sorted(directory.iterdir(), key=lambda path: path.name.casefold(), reverse=True):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        if not path.stat().st_size:
            raise ValueError(f'Empty image: {path}')
        if path.stem in images:
            raise ValueError(f'Photo filenames must have unique stems in {directory.name}: {path.stem}')
        images[path.stem] = path
    return images

def image_url(path):
    return quote(path.relative_to(ROOT).as_posix())

def make_manifest():
    catalog = json.loads((ROOT / 'data/catalog.json').read_text())
    photos = index_images(ROOT / 'assets/photos')
    large_images = index_images(ROOT / 'assets/large')
    by_id = {}
    for photo_id in photos.keys() | large_images.keys():
        thumbnail = photos.get(photo_id)
        large = large_images.get(photo_id)
        source = thumbnail or large
        photo = {'id': photo_id, 'filename': source.name}
        if thumbnail and large:
            # Explicit pairs are already prepared by the owner. Preserve their bytes and URLs.
            photo['src'] = image_url(thumbnail)
            photo['large'] = image_url(large)
        else:
            # A single uploaded file is the original, regardless of the upload directory.
            photo['src'] = 'assets/thumbnails/' + quote(photo_id + '.webp')
            photo['large'] = image_url(source)
        by_id[photo_id] = photo
    imported_ids = [photo['id'] for photo in catalog['photos']]
    missing = set(imported_ids) - by_id.keys()
    if missing:
        raise ValueError(f'Imported photos missing from assets/photos and assets/large: {sorted(missing)[:5]}')
    imported_set = set(imported_ids)
    new_ids = sorted((photo_id for photo_id in by_id if photo_id not in imported_set),
                     key=lambda photo_id: by_id[photo_id]['filename'].casefold(), reverse=True)
    rows = [new_ids[index:index + 3] for index in range(0, len(new_ids), 3)] + catalog['rows']
    if set(photo_id for row in rows for photo_id in row) != set(by_id):
        raise ValueError('Row grouping and photo catalog do not match')
    for row in rows:
        if not 1 <= len(row) <= 3:
            raise ValueError('Each row must contain between one and three photos')
    return {'version': 1, 'photos': [by_id[photo_id] for photo_id in new_ids + imported_ids], 'rows': rows}

def generate_thumbnails(manifest, output):
    count = 0
    for photo in manifest['photos']:
        if not photo['src'].startswith('assets/thumbnails/'):
            continue
        source = ROOT / unquote(photo['large'])
        target = output / unquote(photo['src'])
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with Image.open(source) as original:
                # Use a still first frame in the grid; the original keeps its animation in the viewer.
                image = ImageOps.exif_transpose(original).convert('RGBA')
                edge = min(THUMBNAIL_SIZE, image.width, image.height)
                thumbnail = ImageOps.fit(image, (edge, edge), method=Image.Resampling.LANCZOS)
                thumbnail.save(target, 'WEBP', quality=78, method=4,
                               icc_profile=original.info.get('icc_profile', b''))
        except (OSError, ValueError) as error:
            raise ValueError(f'Cannot generate thumbnail for {source.name}: {error}') from error
        count += 1
    return count

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
    if (ROOT / 'assets/photos').is_dir():
        shutil.copytree(ROOT / 'assets/photos', output / 'assets/photos')
    if (ROOT / 'assets/large').is_dir():
        shutil.copytree(ROOT / 'assets/large', output / 'assets/large')
    generated = generate_thumbnails(manifest, output)
    (output / 'data').mkdir()
    (output / 'data/photos.json').write_text(json.dumps(manifest, ensure_ascii=False, separators=(',', ':')))
    shutil.copy2(ROOT / 'data/visibility.json', output / 'data/visibility.json')
    (output / '.nojekyll').touch()
    print(f'Built {len(manifest["photos"])} photos in {len(manifest["rows"])} rows; '
          f'{len(visibility["hidden"])} hidden IDs; {generated} thumbnails generated.')

if __name__ == '__main__':
    build()
