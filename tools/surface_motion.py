"""Generate opt-in native material animation from the user's installed HL2.

Original code: MIT. Generated material definitions retain Valve's original
parameters and are derived game content, not covered by our MIT grant.
"""
from pathlib import Path
import hashlib
import json
import re
from vpk import read_vpk

ROOT = Path(__file__).resolve().parents[1]
GAME = Path(r'D:/Steam/steamapps/common/Half-Life 2/hl2')
# Preserve tokens and duplicate keys; comments must not count as declarations.
TOKEN = re.compile(r'//[^\r\n]*|/\*.*?\*/|"[^"\r\n]*"|[{}]|[^\s{}"]+', re.S)
WORLD = {'brick', 'concrete', 'metal', 'plaster', 'wood', 'tile', 'nature',
         'ground', 'stone', 'plasterwall', 'ceiling', 'floor', 'building_template'}


def tokens(source):
    return [m for m in TOKEN.finditer(source) if not m[0].startswith(('//', '/*'))]


def animate(name, source):
    """Return an augmented VMT, or None for unsupported/special materials."""
    parts = name.lower().split('/')
    model = len(parts) > 2 and parts[1] == 'models' and (
        parts[2].startswith('props') or parts[2] == 'weapons')
    if not model and (len(parts) < 3 or parts[1] not in WORLD):
        return None
    ts = tokens(source)
    values = [m[0].strip('"').lower() for m in ts]
    if len(values) < 4 or values[1] != '{' or values[-1] != '}':
        return None
    shader = values[0]
    allowed = {'vertexlitgeneric'} if model else {'lightmappedgeneric', 'worldvertextransition'}
    if shader not in allowed or '$basetexture' not in values:
        return None
    # Never overwrite authored animation, atlas offsets, decals or cutout masks.
    excluded = {'proxies', '$translucent', '$alphatest', '$decal', '$additive',
                '$basetexturetransform', '$basetexturetransform2',
                '$bumptransform', '$bumptransform2', '$envmapmasktransform'}
    if any(x in values for x in excluded):
        return None
    depth = 0
    for i, v in enumerate(values[1:], 1):
        depth += (v == '{') - (v == '}')
        if depth < 0 or (depth == 0 and i != len(values) - 1):
            return None
    if depth:
        return None
    seed = int.from_bytes(hashlib.sha256(name.lower().encode()).digest()[:4], 'little')
    phase = (seed % 1000) / 137.0
    period = 8.0 + ((seed >> 10) % 1000) / 200.0
    # World UVs extend far beyond 0..1. Even modest scale/rotation can therefore
    # move whole facades by metres. Keep those terms tiny, not just the drift.
    scale = 0.006 if model else 0.0012
    drift = 0.003 if model else 0.0035
    rotate = 0.12 if model else 0.006
    lines = ['\n// Xenesthesia: animate UVs in the material, before scene projection.',
             '"$xen_center" "[0.5 0.5]"', '"$xen_scale" "[1 1]"',
             '"$xen_shift" "[0 0]"', '"$xen_rotate" "0"',
             f'"$xen_phase" "{phase:.4f}"',
             '"$xen_a" "0"', '"$xen_b" "0"', '"Proxies"', '{']
    # Static props can bind a renderable with no C_BaseEntity. HL2's EntityRandom
    # dereferences that entity without checking it, so use only for viewmodels.
    if model and parts[2] == 'weapons' and len(parts) > 3 and parts[3].startswith('v_'):
        lines += ['"EntityRandom" { "scale" "8" "resultVar" "$xen_phase" }']
    for result, amplitude, base, rate in [
        ('$xen_scale[0]', scale, 1, 1.0),
        ('$xen_scale[1]', scale, 1, 1.29),
        ('$xen_shift[0]', drift, 0, 1.71),
        ('$xen_shift[1]', drift, 0, 1.13),
        ('$xen_rotate', rotate, 0, 1.53),
    ]:
        # Two slow, incommensurate pulses give each axis an evolving rhythm.
        # Sum their bounded amplitudes; the total never exceeds amplitude.
        for weight, frequency, baseline, target in [
            (0.65, 1.0, base, '$xen_a'), (0.35, 1.61803399, 0, '$xen_b')
        ]:
            amount = amplitude * weight
            lines.append(f'"Sine" {{ "sinePeriod" "{period*rate*frequency:.6f}" '
                         f'"sineMin" "{baseline-amount:.6f}" "sineMax" "{baseline+amount:.6f}" '
                         f'"timeOffset" "$xen_phase" "resultVar" "{target}" }}')
        lines.append(f'"Add" {{ "srcVar1" "$xen_a" "srcVar2" "$xen_b" "resultVar" "{result}" }}')
    transforms = ['$basetexturetransform']
    # HL2's WorldVertexTransition shares BASETEXTURETRANSFORM for both layers.
    if '$bumpmap' in values:
        transforms.append('$bumptransform')
    if '$bumpmap2' in values:
        transforms.append('$bumptransform2')
    if '$envmapmask' in values:
        transforms.append('$envmapmasktransform')
    for target in transforms:
        lines.append(f'"TextureTransform" {{ "centerVar" "$xen_center" '
                     f'"scaleVar" "$xen_scale" "translateVar" "$xen_shift" '
                     f'"rotateVar" "$xen_rotate" "resultVar" "{target}" }}')
    lines.append('}\n')
    return source[:ts[-1].start()] + '\n'.join(lines) + source[ts[-1].start():]


def build(content):
    content = Path(content).resolve()
    record_path = ROOT / 'artifacts/surface-materials.json'
    previous = json.loads(record_path.read_text()) if record_path.exists() else {}
    entries, read = read_vpk(GAME / 'hl2_misc_dir.vpk')
    records = {}
    for name in sorted(entries):
        if not name.startswith('materials/') or not name.endswith('.vmt'):
            continue
        raw = read(name)
        source = raw.decode('utf8', errors='strict').replace('\r\r\n', '\n')
        out = animate(name, source)
        if out is None:
            continue
        target = content / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(out, encoding='utf8', newline='\n')
        records[name] = hashlib.sha256(raw).hexdigest()
    # Only remove outputs named by our previous generation manifest. Never touch
    # unrelated user files or the native post-process materials.
    for name in previous.keys() - records.keys():
        target = (content / name).resolve()
        if not target.is_relative_to(content / 'materials') or target.suffix != '.vmt' or 'dev' in target.parts:
            raise ValueError(f'Unsafe generated-material path: {name}')
        target.unlink(missing_ok=True)
    record_path.write_text(json.dumps(records, indent=2)+'\n')
    print(f'Animated {len(records)} installed HL2 materials; textures remain in the base game.')


if __name__ == '__main__':
    build(ROOT / 'content')
