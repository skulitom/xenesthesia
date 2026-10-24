"""Verify the real downloaded Workshop archive; does not publish or alter Steam."""
from pathlib import Path
import hashlib
import json
import sys
from datetime import datetime, timezone
from vpk import read_vpk

ROOT = Path(__file__).resolve().parents[1]

def verify(folder):
    folder = Path(folder).resolve(strict=True)
    record_path = ROOT / 'artifacts/workshop-item.json'
    record = json.loads(record_path.read_text(encoding='utf-8-sig'))
    if folder.name != str(record['published_file_id']):
        raise ValueError('Download folder does not match the recorded Xenesthesia item.')
    archive = folder / 'workshop_dir.vpk'
    entries, read = read_vpk(archive)
    expected = json.loads((ROOT / 'artifacts/build-manifest.json').read_text())
    if set(entries) != set(expected):
        raise ValueError(f'Download path mismatch: missing={set(expected)-set(entries)}, extra={set(entries)-set(expected)}')
    for name, digest in expected.items():
        if hashlib.sha256(read(name)).hexdigest() != digest:
            raise ValueError(f'Download differs: {name}')
    record['downloaded_files_verified'] = len(entries)
    record['download_verified_utc'] = datetime.now(timezone.utc).isoformat()
    record['download_folder'] = str(folder)
    record['download_archive_hashes'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.glob('*.vpk'))}
    record_path.write_text(json.dumps(record, indent=2)+'\n')
    print(f'Verified all {len(entries)} downloaded runtime files. Native activation remains a separate check.')

if __name__ == '__main__':
    verify(sys.argv[1])
