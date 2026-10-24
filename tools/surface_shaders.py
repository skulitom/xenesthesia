"""Patch native generic/world vertex paths without changing their combo ABI.

Original patch/build logic: MIT. Valve-derived compiled shaders retain SDK terms.
The pinned single-player sources match retail HL2; newer multiplayer sources do
not have compatible generic shader combo indices.
"""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import subprocess
import urllib.request
from human_pulse import patch_local_pulse

ROOT = Path(__file__).resolve().parents[1]
SHADERS = {
    'vertexlit_and_unlit_generic_vs20.fxc': ('20b', '30'),
    'vertexlit_and_unlit_generic_bump_vs20.fxc': ('20b', '30'),
    'lightmappedgeneric_vs20.fxc': ('20b',),
    'lightmappedgeneric_flashlight_vs20.fxc': ('20b',),
}


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f'SDK patch anchor changed: {old}')
    return source.replace(old, new, 1)


def patch_shader(name, source):
    generic = name.startswith('vertexlit_and_unlit_generic')
    header = 'xen_human_pulse.h' if generic else 'xen_world_colour.h'
    source = replace_once(source, 'VS_OUTPUT main(', f'#include "{header}"\n\nVS_OUTPUT main(')
    if generic:
        # The three pickup VMTs use the non-bumped generic family. Keep their
        # extra pre-skin transform out of the tightly packed SM2 bump path.
        if '_bump_' not in name:
            source = patch_local_pulse(source)
        # The old SP file used the Xbox/legacy dual register annotation.
        # PC FXC uses vertex sampler s0, as the newer SDK skin shader does.
        source = replace_once(source, 'register( D3DVERTEXTEXTURESAMPLER0, s0 )', 'register( s0 )')
        source = replace_once(source, '\t// Transform into projection space', '''
    float xenMarker = cBaseTexCoordTransform[0].w;
    bool xenHuman = xenMarker >= 1000.0 && xenMarker < 1004.0;
    float3 xenOrigin = float3(cBaseTexCoordTransform[0].x,
                             cBaseTexCoordTransform[1].y, cBaseTexCoordTransform[1].w);
    if (xenHuman && xenMarker < 1002.0) XenNpcPulseWorld(worldPos, worldNormal, xenOrigin, xenMarker);
    if (xenMarker >= 1002.0 && xenMarker < 1003.0)
        worldPos += worldNormal * (smoothstep(52.0, 61.0, v.vPos.z) * (xenMarker - 1002.0) * 6.0);
\t// Transform into projection space''')
        field = ('baseTexCoord2_tangentSpaceVertToEyeVectorXY' if '_bump_' in name else 'baseTexCoord')
        detail = 'detailTexCoord_atten3' if '_bump_' in name else 'detailTexCoord'
        # Marked transforms carry metadata, never actual UV transforms.
        # Restore UVs before assignment to HALF2 to retain full precision.
        for target, transform in [(field, 'cBaseTexCoordTransform'), (detail, 'cDetailTexCoordTransform')]:
            for i, axis in enumerate('xy'):
                anchor = f'o.{target}.{axis} = dot( v.vTexCoord0, {transform}[{i}] );'
                source = replace_once(source, anchor,
                    f'o.{target}.{axis} = xenHuman ? v.vTexCoord0.{axis} : dot( v.vTexCoord0, {transform}[{i}] );')
    else:
        flashlight = 'flashlight' in name
        guard = '!SEAMLESS && DETAIL' if flashlight else '!SEAMLESS && !RELIEF_MAPPING && !FASTPATH'
        transform = 'cNormalMapOrDetailTexCoordTransform' if flashlight else 'cDetailOrBumpTexCoordTransform'
        field = 'detailCoords' if flashlight else 'detailOrBumpAndEnvmapMaskTexCoord.xy'
        source = replace_once(source, '\treturn o;', f'''
#if {guard}
    if (XenWorldColour(cBaseTexCoordTransform[0], {transform}[0]))
        o.{field} = XenWorldColourUV(worldPos);
    if (XenSignEcho(cBaseTexCoordTransform[0], {transform}[0]))
    {{
        // LightmappedGeneric has no independent detail transform. For opted-in
        // signs the base matrix carries the echo transform; restore the base
        // sample so alpha masks, borders and original lettering stay fixed.
        o.{field} = o.baseTexCoord.xy;
        o.baseTexCoord.xy = v.vBaseTexCoord.xy;
    }}
#endif
\treturn o;''')
    return source


def build(content, stock_read):
    pin = json.loads((ROOT/'research/surface-sdk-files.json').read_text())
    cache = ROOT/'artifacts/private/surface-sdk-clean'
    work = ROOT/'artifacts/private/surface-build'
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
        if name in SHADERS:
            raw = patch_shader(name, raw.decode('cp1252')).encode('cp1252')
        (work/name).write_bytes(raw)
    for name in ('xen_human_pulse.h', 'xen_world_colour.h'):
        shutil.copyfile(ROOT/'src'/name, work/name)
    compiler = ROOT/'tools/ShaderCompile2.exe'
    expected = 'df13601822a642d1238d55e65522842fd776911f9e76c9fea1f4cfdf6f220230'
    if not compiler.exists() or hashlib.sha256(compiler.read_bytes()).hexdigest() != expected:
        raise RuntimeError('Run verified tools/bootstrap.ps1 before building surface shaders.')
    with (ROOT/'artifacts/private/surface-compile.log').open('w') as output:
        for source_name, versions in SHADERS.items():
            print(f'Compiling {source_name}...', flush=True)
            for version in versions:
                subprocess.run([str(compiler), '-ver', version, '-types', 'vs', '-threads', '12',
                                '-shaderpath', str(work), '-force', str(work/source_name)],
                               stdout=output, stderr=subprocess.STDOUT, check=True)
                suffix = '20' if version == '20b' else '30'
                name = 'shaders/fxc/'+source_name.replace('_vs20.fxc', f'_vs{suffix}.vcs')
                raw = (work/name).read_bytes()
                if struct.unpack_from('<6I', raw) != struct.unpack_from('<6I', stock_read(name)):
                    raise ValueError(f'Native shader combo layout changed: {name}')
                target = Path(content)/name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
    print('Built generic NPC and continuous world colour paths; native combo layouts verified.')
