"""Experimental classic zombie/headcrab inflation using the native VortWarp ABI.

Original build/patch code: MIT. Compiled shaders include Valve SDK code under
third_party/valve-source-sdk/LICENSE, not MIT. No replacement engine binary.
"""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import subprocess
import urllib.request
import human_pulse

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = {'materials/models/zombie_classic/zombie_classic_sheet.vmt',
             'materials/models/headcrab_classic/headcrabsheet.vmt'}
ANCHOR = '\tWorldSpaceVertexProcess( g_Time, modelOrigin, worldPos, worldNormal, worldTangentS, worldTangentT );'
PATCH = '''\t// Xenesthesia marker >=2: small normal expansion after skinning/flex.
\t// Stock 0..1 teleport animation retains the original implementation below.
\tif (g_Time >= 2.0)
\t{
\t\tworldPos += worldNormal * (g_Time - 2.0);
\t}
\telse
\t{
''' + ANCHOR + '\n\t}'


def material(name, source, token_list):
    if name not in MATERIALS:
        return None
    ts = token_list
    values = [t[0].strip('"').lower() for t in ts]
    if values[0] != 'vertexlitgeneric' or any(v in values for v in
            ('proxies', '$alphatest', '$translucent', '$additive', '$warpparam')):
        raise ValueError(f'NPC material changed; review before overriding {name}')
    extra = '''
// Xenesthesia experimental body pulse: original game textures, no face UV drift.
"$warpparam" "2.1"
"$xen_pulsephase" "0"
"Proxies"
{
    "EntityRandom" { "scale" "5" "resultVar" "$xen_pulsephase" }
    "Sine" { "sinePeriod" "4.7" "sineMin" "2.04" "sineMax" "2.75" "timeOffset" "$xen_pulsephase" "resultVar" "$warpparam" }
}
'''
    result = source[:ts[-1].start()] + extra + source[ts[-1].start():]
    return '"VortWarp"' + result[ts[0].end():]


def build(content, stock_read):
    pin = json.loads((ROOT/'research/npc-sdk-files.json').read_text())
    cache = ROOT/'artifacts/private/npc-sdk-clean'
    work = ROOT/'artifacts/private/npc-build'
    cache.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    for name, info in pin['files'].items():
        if Path(name).name != name:
            raise ValueError('Unsafe SDK cache name')
        original = cache/name
        if not original.exists():
            url = f'https://raw.githubusercontent.com/ValveSoftware/source-sdk-2013/{pin["commit"]}/{info["path"]}'
            raw = urllib.request.urlopen(url, timeout=30).read()
            if hashlib.sha256(raw).hexdigest() != info['sha256']:
                raise ValueError(f'Unexpected SDK source: {name}')
            original.write_bytes(raw)
        raw = original.read_bytes()
        if hashlib.sha256(raw).hexdigest() != info['sha256']:
            raise ValueError(f'SDK cache hash mismatch: {name}')
        (work/name).write_bytes(raw)
    shader = work/'vortwarp_vs20.fxc'
    source = shader.read_text()
    if source.count(ANCHOR) != 1:
        raise ValueError('SDK shader patch anchor changed')
    shader.write_text(source.replace(ANCHOR, PATCH))
    shutil.copyfile(ROOT/'src/xen_human_pulse.h', work/'xen_human_pulse.h')
    for name in human_pulse.SHADERS:
        target = work/name
        source = target.read_bytes().decode('cp1252')
        target.write_bytes(human_pulse.patch_shader(name, source).encode('cp1252'))
    compiler = ROOT/'tools/ShaderCompile2.exe'
    expected = 'df13601822a642d1238d55e65522842fd776911f9e76c9fea1f4cfdf6f220230'
    if not compiler.exists() or hashlib.sha256(compiler.read_bytes()).hexdigest() != expected:
        raise RuntimeError('Run the verified tools/bootstrap.ps1 before building NPC shaders.')
    log = ROOT/'artifacts/private/npc-compile.log'
    with log.open('w') as output:
        for source_name in ['vortwarp_vs20.fxc', *human_pulse.SHADERS]:
            for version in ['20b', '30']:
                subprocess.run([str(compiler), '-ver', version, '-types', 'vs', '-threads', '2',
                                '-shaderpath', str(work), '-force', str(work/source_name)],
                               stdout=output, stderr=subprocess.STDOUT, check=True)
            for version in ['20', '30']:
                name = 'shaders/fxc/'+source_name.lower().replace('_vs20.fxc',f'_vs{version}.vcs')
                raw = (work/name).read_bytes()
                # Preserve the engine's combo-index contract, not merely syntax.
                if struct.unpack_from('<6I', raw) != struct.unpack_from('<6I', stock_read(name)):
                    raise ValueError(f'Native shader combo layout changed: {name}')
                target = Path(content)/name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
    legal = Path(content)/'xenesthesia/licenses'
    legal.mkdir(parents=True, exist_ok=True)
    for source, target in [('LICENSE', 'valve-sdk-license.txt'),
                           ('thirdpartylegalnotices.txt', 'valve-sdk-thirdpartylegalnotices.txt')]:
        shutil.copyfile(ROOT/'third_party/valve-source-sdk'/source, legal/target)
    print('Built experimental classic and human NPC pulses; native combo layouts verified.')
