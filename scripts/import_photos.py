"""Import observed Weibo image URLs. No authentication or browser credentials."""
import concurrent.futures
import json
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def download(photo):
    destination = ROOT / 'assets/photos' / photo['filename']
    if destination.exists() and destination.stat().st_size:
        return None
    for attempt in range(4):
        try:
            result = subprocess.run(['curl', '--fail', '--location', '--silent',
                '--show-error', '--max-time', '35', '--user-agent', 'Mozilla/5.0',
                '--referer', 'https://m.weibo.cn/', photo['src']],
                capture_output=True, check=True)
            content = result.stdout
            from PIL import Image
            import io
            with Image.open(io.BytesIO(content)) as image:
                image.verify()
            destination.write_bytes(content)
            return None
        except Exception as error:
            if attempt == 3:
                return {'id': photo['id'], 'error': str(error)}
            time.sleep(1 + attempt * 2)

if __name__ == '__main__':
    photos = json.loads((ROOT / 'reference-photos.json').read_text())
    (ROOT / 'assets/photos').mkdir(parents=True, exist_ok=True)
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for count, error in enumerate(pool.map(download, photos), 1):
            if error:
                errors.append(error)
                if len(errors) <= 3:
                    print(error, flush=True)
            if count % 100 == 0 or count == len(photos):
                print(f'{count}/{len(photos)} checked; {len(errors)} failed', flush=True)
    (ROOT / 'reference/import-errors.json').write_text(json.dumps(errors, indent=2))
    if errors:
        raise SystemExit(f'{len(errors)} photos failed to import')
