"""Stage a local, reviewable release candidate. No Steam calls or upload code."""
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import hashlib
import json
import shutil
import subprocess
import zipfile

from vpk import read_vpk

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prepare():
    media = json.loads((ROOT / 'artifacts/release/gameplay-media.json').read_text())
    archive_hash = sha((ROOT / 'content.vpk').read_bytes())
    if media['runtime_sha256'] != archive_hash or media['generated_art_used']:
        raise RuntimeError('Release media must show the current build and use no generated artwork.')
    for name, evidence in media['images'].items():
        if sha((ROOT / evidence['source']).read_bytes()) != evidence['sha256']:
            raise ValueError(f'Release screenshot differs from recorded capture: {name}')
    archive = ROOT / 'content.vpk'
    manifest = json.loads((ROOT / 'artifacts/build-manifest.json').read_text())
    entries, read = read_vpk(archive)
    if set(entries) != set(manifest):
        raise ValueError('Archive and build manifest list different files.')
    payloads = {}
    for name, expected in manifest.items():
        path = PurePosixPath(name)
        if (path.is_absolute() or '..' in path.parts or ':' in name or '\\' in name
                or path.suffix not in {'.vmt', '.vcs', '.cfg', '.vtf', '.txt'}):
            raise ValueError(f'Unexpected runtime path: {name}')
        if path.suffix == '.vtf' and name not in {
                'materials/xenesthesia/prism.vtf', 'materials/xenesthesia/weave.vtf',
                'materials/xenesthesia/eddy_normal.vtf'}:
            raise ValueError(f'Unexpected texture: {name}')
        if path.suffix == '.txt' and name not in {
                'xenesthesia/licenses/valve-sdk-license.txt',
                'xenesthesia/licenses/valve-sdk-thirdpartylegalnotices.txt'}:
            raise ValueError(f'Unexpected runtime text: {name}')
        body = read(name)
        if sha(body) != expected or body != (ROOT / 'content' / name).read_bytes():
            raise ValueError(f'Stale or corrupt runtime content: {name}')
        payloads[name] = body

    # Explicit allowlist: no private backups, saves, test harness or compiler.
    review_files = {
        'REVIEW.md': 'artifacts/release/REVIEW.md',
        'PUBLISHING.md': 'artifacts/release/PUBLISHING.md',
        'INSTALL.txt': 'artifacts/release/INSTALL.txt',
        'LICENSE': 'LICENSE',
        'NOTICE.md': 'NOTICE.md',
        'licenses/Valve-SDK-LICENSE.txt': 'third_party/valve-source-sdk/LICENSE',
        'licenses/Valve-SDK-thirdpartylegalnotices.txt': 'third_party/valve-source-sdk/thirdpartylegalnotices.txt',
        'VALIDATION.md': 'artifacts/VALIDATION.md',
        'COVERAGE.md': 'artifacts/release/COVERAGE.md',
        'workshop-description.txt': 'artifacts/workshop-description.txt',
        'gameplay-media.json': 'artifacts/release/gameplay-media.json',
        'CURRENT-VALIDATION.md': 'artifacts/campaign-coverage/VALIDATION.md',
    }
    review_files.update({f'media/{name}': evidence['source']
                         for name, evidence in media['images'].items()})
    for name, source in review_files.items():
        if not (ROOT / source).is_file():
            raise FileNotFoundError(source)
        if (name.startswith('media/')
                and (ROOT / source).stat().st_size >= 1_000_000):
            raise ValueError(f'Preview image exceeds conservative 1 MB limit: {name}')

    now = datetime.now(timezone.utc)
    archive_hash = sha(archive.read_bytes())
    destination = ROOT / 'dist' / f'xenesthesia-release-{now:%Y%m%dT%H%M%S}-{archive_hash[:8]}'
    destination.mkdir(parents=True, exist_ok=False)
    content_root = destination / 'workshop-content'
    for name, body in payloads.items():
        target = content_root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    for name, source in review_files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)

    manual_zip = destination / 'xenesthesia-manual-install.zip'
    with zipfile.ZipFile(manual_zip, 'w', zipfile.ZIP_DEFLATED) as package:
        package.write(archive, 'xenesthesia.vpk')
        for name in ['INSTALL.txt', 'LICENSE', 'NOTICE.md', 'licenses/Valve-SDK-LICENSE.txt', 'licenses/Valve-SDK-thirdpartylegalnotices.txt']:
            package.write(destination / name, name)
    with zipfile.ZipFile(manual_zip) as package:
        if package.testzip() or sha(package.read('xenesthesia.vpk')) != archive_hash:
            raise ValueError('Manual-install ZIP verification failed.')
        if set(package.namelist()) != {'xenesthesia.vpk', 'INSTALL.txt', 'LICENSE', 'NOTICE.md', 'licenses/Valve-SDK-LICENSE.txt', 'licenses/Valve-SDK-thirdpartylegalnotices.txt'}:
            raise ValueError('Unexpected file in manual-install ZIP.')
    for name, expected in manifest.items():
        if sha((content_root / name).read_bytes()) != expected:
            raise ValueError(f'Staged runtime verification failed: {name}')

    metadata = {
        'status': 'release candidate; owner authorized Workshop publication on 2026-10-24',
        'prepared_utc': now.isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'tracked_working_changes': subprocess.run(['git', 'diff', '--quiet', 'HEAD'], cwd=ROOT).returncode != 0,
        'runtime_sha256': archive_hash,
        'runtime_files': len(payloads),
        'files': {p.relative_to(destination).as_posix(): sha(p.read_bytes())
                  for p in sorted(destination.rglob('*')) if p.is_file()},
    }
    (destination / 'manifest.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf8')
    print(destination)
    print(f'Verified {len(payloads)} runtime files and the manual-install ZIP. Nothing uploaded.')
    return destination


if __name__ == '__main__':
    prepare()
