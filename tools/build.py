"""Build surface colour/motion and a content-only, offline Workshop archive."""
from pathlib import Path
import hashlib
import json
import subprocess
from vpk import read_vpk
from surface_motion import build as build_surface_motion
from prism_texture import build as build_prism_texture
from lab_textures import build as build_lab_textures

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'content'

def main():
    (CONTENT / 'cfg').mkdir(parents=True, exist_ok=True)
    # Retire the camera-depth colour path completely, including its bloom hook.
    for old in ['materials/dev/engine_post.vmt', 'materials/dev/bloomadd.vmt',
                'shaders/fxc/xenesthesia_ps20b.vcs']:
        (CONTENT / old).unlink(missing_ok=True)
    build_prism_texture(CONTENT)
    build_lab_textures(CONTENT)
    build_surface_motion(CONTENT)
    package()


def package():
    """Pack and verify the current generated content without compiling it."""
    manifest = {p.relative_to(CONTENT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(CONTENT.rglob('*')) if p.is_file()}
    if any(name != name.lower() for name in manifest):
        raise RuntimeError('Runtime paths must be lowercase; Valve VPK normalizes names.')
    packer = Path(r'D:\Steam\steamapps\common\Half-Life 2\bin\vpk.exe')
    subprocess.run([str(packer), str(CONTENT)], check=True)
    entries, read = read_vpk(ROOT/'content.vpk')
    if set(entries) != set(manifest) or any(hashlib.sha256(read(name)).hexdigest() != digest
                                           for name, digest in manifest.items()):
        raise RuntimeError('VPK differs from the built content. Close the test game and rebuild.')
    (ROOT/'artifacts/build-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'Built {len(manifest)} runtime files; archive {(ROOT/"content.vpk").stat().st_size} bytes.')

if __name__ == '__main__':
    main()
