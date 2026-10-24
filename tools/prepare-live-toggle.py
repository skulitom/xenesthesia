"""Prepare exact on/off material trees for the optional local F5 companion.

Never run while HL2 or the companion is using these directories. The VPK is
unchanged; its original-marker-free vertex paths also render stock materials.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from vpk import read_vpk

ROOT = Path(__file__).resolve().parents[1]
GAME = Path('D:/Steam/steamapps/common/Half-Life 2')
# Same volume as the mounted directory: switching uses two atomic renames,
# never thousands of file copies while the game is running.
STATE = GAME/'xenesthesia-live-state'
MOUNT = GAME/'hl2/custom/aa_xenesthesia_live'
OWNER = 'Xenesthesia live toggle v1'


def reset_owned(root):
    root = root.resolve()
    allowed = {STATE.resolve(), MOUNT.resolve()}
    if root not in allowed or not root.is_relative_to(GAME.resolve()):
        raise ValueError('Unexpected live toggle path')
    if root.exists():
        if (root/'.xenesthesia-owned').read_text() != OWNER:
            raise ValueError(f'Unowned directory: {root}')
        shutil.rmtree(root)
    root.mkdir(parents=True)
    (root/'.xenesthesia-owned').write_text(OWNER)


def main():
    running = subprocess.run(['powershell', '-NoProfile', '-Command',
                              "Get-Process hl2,xenesthesia-toggle -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id"],
                             capture_output=True, text=True)
    if running.stdout.strip():
        raise RuntimeError('Close HL2 and its toggle companion before preparing files.')
    _, read = read_vpk(GAME/'hl2/hl2_misc_dir.vpk')
    manifest = json.loads((ROOT/'artifacts/surface-materials.json').read_text())
    # Validate every original and generated file before touching the mount.
    pairs = []
    for name, digest in manifest.items():
        original = read(name)
        if hashlib.sha256(original).hexdigest() != digest:
            raise ValueError(f'Stock material changed: {name}')
        pairs.append((Path(name).relative_to('materials'), original, (ROOT/'content'/name).read_bytes()))
    for root in (STATE, MOUNT):
        reset_owned(root)
    for name, original, modified in pairs:
        for root, data in [(STATE/'off', original), (MOUNT/'materials', modified)]:
            target = root/name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    compiler = Path('C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe')
    subprocess.run([str(compiler), '/nologo', '/target:winexe', '/optimize+',
                    '/out:'+str(STATE/'xenesthesia-toggle.exe'), str(ROOT/'tools/live_toggle.cs')], check=True)
    (STATE/'state.txt').write_text('on')
    (STATE/'materials.json').write_text(json.dumps(manifest, indent=2))
    print(f'Prepared verified on/off copies of {len(pairs)} materials and the local F5 companion.')


if __name__ == '__main__':
    main()
