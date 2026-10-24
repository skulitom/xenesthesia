"""Generate opt-in native material animation from the user's installed HL2.

Original code: MIT. Generated material definitions retain Valve's original
parameters and are derived game content, not covered by our MIT grant.
"""
from pathlib import Path
import hashlib
import json
import re
from vpk import read_vpk
import npc_pulse
import human_pulse
import surface_shaders
import lab_materials

ROOT = Path(__file__).resolve().parents[1]
GAME = Path(r'D:/Steam/steamapps/common/Half-Life 2/hl2')
# Preserve tokens and duplicate keys; comments must not count as declarations.
TOKEN = re.compile(r'//[^\r\n]*|/\*.*?\*/|"[^"\r\n]*"|[{}]|[^\s{}"]+', re.S)
WORLD = {'brick', 'concrete', 'metal', 'plaster', 'wood', 'tile', 'nature',
         'ground', 'stone', 'plasterwall', 'ceiling', 'floor', 'building_template', 'props'}
GRAIN_DETAILS = {'detail/plaster_detail_01', 'detail/noise_detail_01',
                 'detail/metal_detail_01', 'detail/rock_detail_01'}


def tokens(source):
    return [m for m in TOKEN.finditer(source) if not m[0].startswith(('//', '/*'))]


def animate(name, source):
    """Return an augmented VMT, or None for unsupported/special materials."""
    parts = name.lower().split('/')
    rug = name.lower() in lab_materials.RUGS
    overlay = rug or name.lower() in lab_materials.RUNNERS
    carpet = overlay or name.lower() in lab_materials.CARPET_FLOORS
    model = len(parts) > 2 and parts[1] == 'models'
    if not model and not carpet and (len(parts) < 3 or parts[1] not in WORLD):
        return None
    ts = tokens(source)
    values = [m[0].strip('"').lower() for m in ts]
    if len(values) < 4 or values[1] != '{' or values[-1] != '}':
        return None
    shader = values[0]
    allowed = {'vertexlitgeneric', 'unlitgeneric'} if model else {'lightmappedgeneric', 'worldvertextransition'}
    if shader not in allowed or '$basetexture' not in values:
        return None
    # Alpha-tested surfaces can receive MOD2X colour without moving their mask.
    excluded = {'$additive'} if overlay else {'$translucent', '$decal', '$additive'}
    if any(x in values for x in excluded):
        return None
    depth = 0
    for i, v in enumerate(values[1:], 1):
        depth += (v == '{') - (v == '}')
        if depth < 0 or (depth == 0 and i != len(values) - 1):
            return None
    if depth:
        return None
    # Keep an existing Proxies block and append to it. Never create a second one:
    # KeyValues does not combine duplicate blocks reliably.
    proxy_close = None
    depth = 0
    proxy_depth = None
    for i, value in enumerate(values):
        if value == 'proxies' and depth == 1:
            if proxy_depth is not None or proxy_close is not None:
                return None
            if i+1 >= len(values) or values[i+1] != '{':
                return None
            proxy_depth = 2
        if value == '}' and depth == proxy_depth:
            proxy_close = ts[i].start()
            proxy_depth = None
        depth += (value == '{') - (value == '}')
    unsafe_motion = {'proxies', '$alphatest', '$basetexturetransform',
                     '$basetexturetransform2', '$bumptransform', '$bumptransform2',
                     '$envmapmasktransform'}
    # NPC colour is supported; their facial UVs stay intact. Geometric pulses
    # are tested separately instead of sliding eyes/mouths across their faces.
    prop = model and (parts[2].startswith('props') or parts[2] == 'weapons'
                     or parts[2] in {'combine_room', 'combine_apc', 'items'})
    motion = not overlay and name not in human_pulse.PICKUPS and not any(x in values for x in unsafe_motion) and (not model or prop)
    details = [values[i+1].replace('\\', '/') for i, v in enumerate(values[:-1]) if v == '$detail']
    # Standard micrograin layers can be replaced by our own colour+grain field.
    # Special detail blends (cracks, masks, authored animation) remain intact.
    replace_grain = bool(details) and all(d in GRAIN_DETAILS for d in details) and 'proxies' not in values
    colour = ((not details or replace_grain) and '$detailframe' not in values
              and (model or '$seamless_scale' not in values))
    if not motion and not colour:
        return None
    seed = int.from_bytes(hashlib.sha256(name.lower().encode()).digest()[:4], 'little')
    phase = (seed % 1000) / 137.0
    period = 8.0 + ((seed >> 10) % 1000) / 200.0
    if not model:
        phase, period = 0.0, 12.0
    # World UVs extend far beyond 0..1. Even modest scale/rotation can therefore
    # move whole facades by metres. Keep those terms tiny, not just the drift.
    scale = 0.006 if model else 0.0012
    drift = 0.003 if model else 0.0035
    rotate = 0.12 if model else 0.006
    declarations = ['\n// Xenesthesia: surface-local animation, independent of the camera.']
    lines = []
    replacements = []
    if colour:
        params = {'$detail': 'xenesthesia/weave' if rug else 'xenesthesia/prism', '$detailframe': '0',
                  '$detailblendmode': '0', '$detailblendfactor': '0.9',
                  '$detailscale': f'{(1.0 if model or rug else -1337.0):.3f}'}
        for key, value in params.items():
            positions = [i+1 for i, v in enumerate(values[:-1]) if v == key]
            if positions:
                replacements.extend((ts[i].start(), ts[i].end(), f'"{value}"') for i in positions)
            else:
                declarations.append(f'"{key}" "{value}"')
        # Connected world faces share a clock and world coordinates to avoid
        # UV/material seams. Movable objects retain their own UV-local clock.
        colour_fps = (7.0 + ((seed >> 20) % 1000) / 250.0) if model else 8.0
        lines += ['"AnimatedTexture" { "animatedTextureVar" "$detail" '
                  '"animatedTextureFrameNumVar" "$detailframe" '
                  f'"animatedTextureFrameRate" "{colour_fps:.3f}" }}']
    if motion:
        declarations += [
             '"$xen_center" "[0.5 0.5]"', '"$xen_scale" "[1 1]"',
             '"$xen_shift" "[0 0]"', '"$xen_rotate" "0"',
             f'"$xen_phase" "{phase:.4f}"',
             '"$xen_a" "0"', '"$xen_b" "0"']
    # Static props can bind a renderable with no C_BaseEntity. HL2's EntityRandom
    # dereferences that entity without checking it, so use only for viewmodels.
    if motion and model and parts[2] == 'weapons' and len(parts) > 3 and parts[3].startswith('v_'):
        lines += ['"EntityRandom" { "scale" "8" "resultVar" "$xen_phase" }']
    for result, amplitude, base, rate in ([
        ('$xen_scale[0]', scale, 1, 1.0),
        ('$xen_scale[1]', scale, 1, 1.29),
        ('$xen_shift[0]', drift, 0, 1.71),
        ('$xen_shift[1]', drift, 0, 1.13),
        ('$xen_rotate', rotate, 0, 1.53),
    ] if motion else []):
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
    for target in (transforms if motion else []):
        lines.append(f'"TextureTransform" {{ "centerVar" "$xen_center" '
                     f'"scaleVar" "$xen_scale" "translateVar" "$xen_shift" '
                     f'"rotateVar" "$xen_rotate" "resultVar" "{target}" }}')
    inserts = [(ts[-1].start(), ts[-1].start(), '\n'.join(declarations) + '\n')]
    if proxy_close is not None:
        inserts.append((proxy_close, proxy_close, '\n' + '\n'.join(lines) + '\n'))
    else:
        inserts[0] = (*inserts[0][:2], inserts[0][2] + '"Proxies"\n{\n' + '\n'.join(lines) + '\n}\n')
    for start, end, addition in sorted(inserts + replacements, reverse=True):
        source = source[:start] + addition + source[end:]
    return source


def build_materials(content):
    """Generate material definitions independently of compiling native shaders."""
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
        out = lab_materials.tank_material(name, source, tokens)
        if out is None:
            out = npc_pulse.material(name, source, tokens(source))
        if out is None:
            out = animate(name, source)
        human = human_pulse.material(name, out if out is not None else source, tokens)
        if human is not None:
            out = human
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


def build(content):
    build_materials(content)
    _, read = read_vpk(GAME / 'hl2_misc_dir.vpk')
    npc_pulse.build(content, read)
    surface_shaders.build(content, read)


if __name__ == '__main__':
    build(ROOT / 'content')
