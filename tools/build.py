"""Build Xenesthesia's original shader and content-only Workshop archive."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
from vpk import read_vpk
from surface_motion import build as build_surface_motion

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'content'

def material():
    return '''"screenspace_general"
{
    "$pixshader" "xenesthesia_ps20"
    "$basetexture" "_rt_FullFrameFB"
    "$texture2" "_rt_SmallFB1"
    "$linearread_basetexture" "1"
    "$linearread_texture2" "1"
    "$linearwrite" "1"
    "$ignorez" "1"
    "$c0_x" "1"
    "$c0_y" "0"
    "$c0_z" "0"
    "$c0_w" "0.13"
    "$c1_x" "0"
    "$c1_y" "0"
    "$c1_z" "0"
    "$c1_w" "1.08"
    "Proxies"
    {
        "CurrentTime"
        {
            "resultVar" "$c1_x"
        }
    }
}
'''

def main():
    for folder in ['materials/dev', 'shaders/fxc', 'cfg']:
        (CONTENT / folder).mkdir(parents=True, exist_ok=True)
    build_surface_motion(CONTENT)
    compiler = ROOT / 'tools/ShaderCompile2.exe'
    expected = 'df13601822a642d1238d55e65522842fd776911f9e76c9fea1f4cfdf6f220230'
    if hashlib.sha256(compiler.read_bytes()).hexdigest() != expected:
        raise RuntimeError('Unexpected compiler; run the verified bootstrap first.')
    subprocess.run([str(compiler), '-ver', '20b', '-types', 'ps', '-threads', '2',
                    '-shaderpath', str(ROOT/'src'), '-force',
                    str(ROOT/'src/xenesthesia_ps2x.fxc')], check=True)
    shaders = list((ROOT/'src/shaders').rglob('xenesthesia_ps20b.vcs'))
    if len(shaders) != 1:
        raise RuntimeError(f'Expected one compiled shader, found {shaders}')
    shutil.copy2(shaders[0], CONTENT/'shaders/fxc/xenesthesia_ps20b.vcs')
    for name in ['engine_post', 'bloomadd']:
        (CONTENT/f'materials/dev/{name}.vmt').write_text(material(), encoding='ascii')
    manifest = {p.relative_to(CONTENT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(CONTENT.rglob('*')) if p.is_file()}
    (ROOT/'artifacts/build-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    packer = Path(r'D:\Steam\steamapps\common\Half-Life 2\bin\vpk.exe')
    subprocess.run([str(packer), str(CONTENT)], check=True)
    entries, read = read_vpk(ROOT/'content.vpk')
    if set(entries) != set(manifest) or any(hashlib.sha256(read(name)).hexdigest() != digest
                                           for name, digest in manifest.items()):
        raise RuntimeError('VPK differs from the built content. Close the test game and rebuild.')
    print(f'Built {len(manifest)} runtime files; archive {(ROOT/"content.vpk").stat().st_size} bytes.')

if __name__ == '__main__':
    main()
