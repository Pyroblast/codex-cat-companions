#!/usr/bin/env python3
"""Install verified Codex cat pets using only the Python standard library."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
PET_IDS = ('lili', 'taitai', 'kaikai', 'juqian')
FILES = ('pet.json', 'spritesheet.webp')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_source(root, selected):
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    entries = {p['id']: p for p in manifest['pets']}
    for pet in selected:
        entry = entries[pet]
        folder = root / 'pets' / pet
        for name in FILES:
            if digest(folder / name) != entry['files'][name]:
                raise ValueError('Source checksum mismatch: {}/{}'.format(pet, name))
        config = json.loads((folder / 'pet.json').read_text(encoding='utf-8'))
        if (config.get('id') != pet or config.get('spriteVersionNumber') != 2
                or config.get('spritesheetPath') != 'spritesheet.webp'):
            raise ValueError('Invalid pet configuration: ' + pet)
    return entries


def install(root, destination, selected, replace=False):
    """Preflight all pets; skip exact copies and back up explicit replacements."""
    entries = verify_source(root, selected)
    plans = []
    for pet in selected:
        target = destination / pet
        if target.is_symlink():
            raise ValueError('Refusing symlink destination: ' + str(target))
        present = target.exists()
        same = present and target.is_dir() and all(
            (target / name).is_file()
            and digest(target / name) == entries[pet]['files'][name]
            for name in FILES
        )
        if present and not same and not replace:
            raise ValueError('Different pet already exists: {}. Use --replace to back it up first.'.format(target))
        if present and not target.is_dir():
            raise ValueError('Destination is not a directory: ' + str(target))
        plans.append((pet, target, same, present))
    destination.mkdir(parents=True, exist_ok=True)
    results = []
    for pet, target, same, present in plans:
        if same:
            results.append((pet, 'unchanged', None))
            continue
        staging = Path(tempfile.mkdtemp(prefix='.cat-pet-', dir=str(destination)))
        backup = None
        try:
            for name in FILES:
                shutil.copyfile(root / 'pets' / pet / name, staging / name)
                if digest(staging / name) != entries[pet]['files'][name]:
                    raise ValueError('Staged checksum mismatch: ' + pet)
            if present:
                backups = destination.parent / (destination.name + '-backups')
                backups.mkdir(parents=True, exist_ok=True)
                stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
                backup = backups / (pet + '-' + stamp)
                target.rename(backup)
            elif target.exists() or target.is_symlink():
                raise ValueError('Destination appeared during install: ' + str(target))
            try:
                staging.rename(target)
            except Exception:
                if backup is not None and not target.exists():
                    backup.rename(target)
                raise
            results.append((pet, 'installed', str(backup) if backup else None))
        finally:
            # Only remove this invocation's temporary copies, never existing pets.
            if staging.exists():
                shutil.rmtree(staging)
    return results


def main():
    default_home = Path(os.environ.get('CODEX_HOME') or (Path.home() / '.codex')).expanduser()
    parser = argparse.ArgumentParser(description='Install four Codex v2 cat pets (offline, no dependencies).')
    parser.add_argument('--pet', choices=PET_IDS, action='append', help='Install one pet; repeat to select several. Default: all four.')
    parser.add_argument('--dest', type=Path, default=default_home / 'pets', help='Override the pets directory.')
    parser.add_argument('--replace', action='store_true', help='Back up different existing versions before installing.')
    args = parser.parse_args()
    selected = list(dict.fromkeys(args.pet or PET_IDS))
    try:
        results = install(ROOT, args.dest.expanduser().absolute(), selected, args.replace)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('Installation stopped: {}'.format(exc), file=sys.stderr)
        return 1
    for pet, status, backup in results:
        print('{}: {}'.format(pet, status))
        if backup:
            print('  Backup: ' + backup)
    print('Destination: ' + str(args.dest.expanduser().absolute()))
    print('Open Codex Settings > Pets > Refresh, then choose your cat.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
