"""Download higher-resolution renditions, keeping a bounded Pages payload."""
import concurrent.futures
import io
import json
import subprocess
import time
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
TARGET_BYTES = 450 * 1024

def encode(image):
    for edge in [2048, 1600, 1280]:
        resized = image.copy()
        resized.thumbnail((edge, edge), Image.Resampling.LANCZOS)
        for quality in [82, 76, 70]:
            output = io.BytesIO()
            resized.save(output, 'WEBP', quality=quality, method=4)
            if output.tell() <= TARGET_BYTES:
                return output.getvalue()
    return output.getvalue()

def import_photo(photo):
    destination = ROOT / 'assets/large' / (photo['id'] + '.webp')
    if destination.exists():
        with Image.open(destination) as image:
            return {'id': photo['id'], 'width': image.width, 'height': image.height}
    url = photo['src'].replace('/orj480/', '/mw2000/')
    error = None
    for attempt in range(3):
        try:
            result = subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                '--max-time', '50', '--referer', 'https://m.weibo.cn/', url],
                check=True, capture_output=True)
            with Image.open(io.BytesIO(result.stdout)) as source:
                image = ImageOps.exif_transpose(source).convert('RGB')
                data = encode(image)
            temporary = destination.with_suffix('.tmp')
            temporary.write_bytes(data)
            temporary.replace(destination)
            with Image.open(destination) as image:
                return {'id': photo['id'], 'width': image.width, 'height': image.height}
        except Exception as exception:
            error = str(exception)
            time.sleep(attempt + 1)
    return {'id': photo['id'], 'error': error}

if __name__ == '__main__':
    photos = json.loads((ROOT / 'reference-photos.json').read_text())
    (ROOT / 'assets/large').mkdir(parents=True, exist_ok=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for index, result in enumerate(pool.map(import_photo, photos), 1):
            results.append(result)
            if index % 100 == 0 or index == len(photos):
                errors = sum('error' in item for item in results)
                print(f'{index}/{len(photos)} high-resolution photos; {errors} errors', flush=True)
    (ROOT / 'reference/large-import-results.json').write_text(json.dumps(results, indent=2))
    errors = [item for item in results if 'error' in item]
    if errors:
        print(errors[:5], flush=True)
        raise SystemExit(f'{len(errors)} high-resolution imports failed')
