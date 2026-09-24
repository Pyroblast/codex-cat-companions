import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.dest = self.base / 'pets'

    def test_install_all_and_repeat_without_changes(self):
        results = installer.install(ROOT, self.dest, installer.PET_IDS)
        self.assertEqual([r[1] for r in results], ['installed'] * 4)
        before = {}
        for pet in installer.PET_IDS:
            for name in installer.FILES:
                f = self.dest / pet / name
                self.assertEqual(f.read_bytes(), (ROOT / 'pets' / pet / name).read_bytes())
                before[str(f)] = f.stat().st_mtime_ns
        results = installer.install(ROOT, self.dest, installer.PET_IDS)
        self.assertEqual([r[1] for r in results], ['unchanged'] * 4)
        self.assertTrue(all(Path(f).stat().st_mtime_ns == m for f, m in before.items()))

    def test_conflict_preflight_leaves_everything_untouched(self):
        other = self.dest / 'juqian'
        other.mkdir(parents=True)
        (other / 'pet.json').write_text('old')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            installer.install(ROOT, self.dest, installer.PET_IDS)
        self.assertFalse((self.dest / 'lili').exists())
        self.assertEqual((other / 'pet.json').read_text(), 'old')

    def test_replace_backs_up_complete_old_folder(self):
        old = self.dest / 'lili'
        old.mkdir(parents=True)
        (old / 'pet.json').write_text('old')
        (old / 'my-note.txt').write_text('keep me')
        result = installer.install(ROOT, self.dest, ['lili'], replace=True)[0]
        backup = Path(result[2])
        self.assertEqual((backup / 'pet.json').read_text(), 'old')
        self.assertEqual((backup / 'my-note.txt').read_text(), 'keep me')
        self.assertEqual((old / 'pet.json').read_bytes(), (ROOT / 'pets/lili/pet.json').read_bytes())

    def test_install_one_preserves_unrelated_pet(self):
        other = self.dest / 'my-pet'
        other.mkdir(parents=True)
        (other / 'note').write_text('untouched')
        installer.install(ROOT, self.dest, ['taitai'])
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()), ['my-pet', 'taitai'])
        self.assertEqual((other / 'note').read_text(), 'untouched')

    def test_invalid_source_is_rejected_before_destination_write(self):
        source = self.base / 'broken-source'
        pet = source / 'pets/lili'
        pet.mkdir(parents=True)
        (source / 'manifest.json').write_bytes((ROOT / 'manifest.json').read_bytes())
        (pet / 'pet.json').write_text('corrupted')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            installer.install(source, self.dest, ['lili'])
        self.assertFalse(self.dest.exists())

    def test_symlink_destination_is_refused(self):
        target = self.base / 'existing'
        target.mkdir()
        self.dest.mkdir()
        try:
            (self.dest / 'lili').symlink_to(target, target_is_directory=True)
        except OSError:
            self.skipTest('Symlinks not available for this user/platform')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            installer.install(ROOT, self.dest, ['lili'], replace=True)
        self.assertEqual(list(target.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
