import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

from PIL import Image, ImageDraw

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('photo_wall_build', PROJECT / 'scripts/build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PhotoLibraryBuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.previous_root = builder.ROOT
        builder.ROOT = self.root
        (self.root / 'data').mkdir()
        self.write_catalog([], [])
        (self.root / 'data/visibility.json').write_text('{"version":1,"hidden":[]}')
        for name in ['index.html', 'admin.html', 'style.css', 'admin.css', 'gallery.js', 'wall.js', 'admin.js']:
            (self.root / name).write_text('fixture')

    def tearDown(self):
        builder.ROOT = self.previous_root
        self.temporary.cleanup()

    def write_catalog(self, photos, rows):
        (self.root / 'data/catalog.json').write_text(json.dumps({'version': 1, 'photos': photos, 'rows': rows}))

    def image(self, path, size=(2400, 1600), mode='RGB', color='red'):
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        Image.new(mode, size, color).save(destination)
        return destination

    def build(self):
        builder.build()
        return json.loads((self.root / 'dist/data/photos.json').read_text())

    def output_path(self, url):
        return self.root / 'dist' / unquote(url)

    def test_single_upload_creates_thumbnail_and_keeps_original_bytes(self):
        original = self.image('assets/photos/my-photo.jpg')
        before = original.read_bytes()
        photo = self.build()['photos'][0]
        self.assertEqual(photo['large'], 'assets/photos/my-photo.jpg')
        self.assertEqual(original.read_bytes(), before)
        self.assertEqual(self.output_path(photo['large']).read_bytes(), before)
        with Image.open(self.output_path(photo['src'])) as thumbnail:
            self.assertEqual(thumbnail.size, (640, 640))
            self.assertEqual(thumbnail.format, 'WEBP')
        self.assertLess(self.output_path(photo['src']).stat().st_size, len(before))
        self.assertFalse((self.root / 'assets/thumbnails').exists())

    def test_large_directory_alone_accepts_all_supported_formats(self):
        for extension in ['jpg', 'jpeg', 'png', 'webp', 'gif', 'avif']:
            with self.subTest(extension=extension):
                original = self.image(f'assets/large/upload-{extension}.{extension}')
                manifest = self.build()
                photo = next(item for item in manifest['photos'] if item['id'] == f'upload-{extension}')
                self.assertEqual(photo['large'], f'assets/large/{original.name}')
                self.assertTrue(self.output_path(photo['src']).is_file())
                self.assertEqual(self.output_path(photo['large']).read_bytes(), original.read_bytes())

    def test_explicit_pair_preserves_both_files_and_urls(self):
        small = self.image('assets/photos/paired.jpg', size=(320, 320))
        large = self.image('assets/large/paired.png')
        before = {small: small.read_bytes(), large: large.read_bytes()}
        photo = self.build()['photos'][0]
        self.assertEqual(photo, {'id': 'paired', 'filename': 'paired.jpg',
                                'src': 'assets/photos/paired.jpg', 'large': 'assets/large/paired.png'})
        self.assertFalse((self.root / 'dist/assets/thumbnails').exists())
        for original, content in before.items():
            self.assertEqual(original.read_bytes(), content)
            self.assertEqual((self.root / 'dist' / original.relative_to(self.root)).read_bytes(), content)

    def test_existing_rows_duplicates_visibility_and_pairing_stay_unchanged(self):
        for photo_id in ['first', 'second']:
            self.image(f'assets/photos/{photo_id}.jpg', size=(480, 480))
            self.image(f'assets/large/{photo_id}.webp')
        rows = [['second'], ['first', 'second']]
        self.write_catalog([{'id': name, 'filename': name + '.jpg'} for name in ['second', 'first']], rows)
        visibility = {'version': 1, 'hidden': ['first']}
        (self.root / 'data/visibility.json').write_text(json.dumps(visibility))
        manifest = self.build()
        self.assertEqual(manifest['rows'], rows)
        self.assertEqual([photo['id'] for photo in manifest['photos']], ['second', 'first'])
        self.assertEqual(json.loads((self.root / 'dist/data/visibility.json').read_text()), visibility)
        self.assertFalse((self.root / 'dist/assets/thumbnails').exists())

    def test_new_photos_are_sorted_before_original_rows(self):
        self.image('assets/photos/original.jpg')
        self.write_catalog([{'id': 'original', 'filename': 'original.jpg'}], [['original']])
        self.image('assets/photos/2026-10-14.jpg')
        self.image('assets/large/2026-10-15.png')
        self.assertEqual(self.build()['rows'], [['2026-10-15', '2026-10-14'], ['original']])

    def test_small_transparent_images_are_not_upscaled(self):
        self.image('assets/photos/tiny.png', size=(80, 120), mode='RGBA', color=(0, 0, 0, 0))
        photo = self.build()['photos'][0]
        with Image.open(self.output_path(photo['src'])) as thumbnail:
            self.assertEqual(thumbnail.size, (80, 80))
            self.assertEqual(thumbnail.convert('RGBA').getpixel((40, 40))[3], 0)

    def test_animated_original_keeps_animation_with_still_thumbnail(self):
        destination = self.root / 'assets/photos/animated.gif'
        destination.parent.mkdir(parents=True)
        first = Image.new('RGB', (800, 800), 'red')
        first.save(destination, save_all=True, append_images=[Image.new('RGB', (800, 800), 'blue')], duration=200, loop=0)
        photo = self.build()['photos'][0]
        with Image.open(self.output_path(photo['large'])) as original:
            self.assertEqual(original.n_frames, 2)
        with Image.open(self.output_path(photo['src'])) as thumbnail:
            self.assertEqual(getattr(thumbnail, 'n_frames', 1), 1)

    def test_thumbnail_respects_exif_orientation(self):
        destination = self.root / 'assets/photos/rotated.jpg'
        destination.parent.mkdir(parents=True)
        image = Image.new('RGB', (1200, 800), 'red')
        ImageDraw.Draw(image).rectangle((600, 0, 1200, 800), fill='blue')
        exif = Image.Exif()
        exif[274] = 6
        image.save(destination, exif=exif)
        photo = self.build()['photos'][0]
        with Image.open(self.output_path(photo['src'])) as thumbnail:
            self.assertGreater(thumbnail.getpixel((320, 100))[0], 200)
            self.assertGreater(thumbnail.getpixel((320, 540))[2], 200)

    def test_special_characters_in_filenames_are_url_encoded(self):
        self.image('assets/photos/夏日 #1.png')
        photo = self.build()['photos'][0]
        self.assertIn('%20%23', photo['src'])
        self.assertTrue(self.output_path(photo['src']).is_file())
        self.assertTrue(self.output_path(photo['large']).is_file())

    def test_duplicate_ids_in_the_same_directory_are_rejected(self):
        self.image('assets/large/duplicate.jpg')
        self.image('assets/large/duplicate.png')
        with self.assertRaisesRegex(ValueError, 'unique stems'):
            builder.build()

    def test_corrupt_new_upload_fails_with_filename(self):
        destination = self.root / 'assets/photos/broken.jpg'
        destination.parent.mkdir(parents=True)
        destination.write_bytes(b'not an image')
        with self.assertRaisesRegex(ValueError, 'broken.jpg'):
            builder.build()


if __name__ == '__main__':
    unittest.main()
