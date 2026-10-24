"""Read-only asset coverage inventory; this is not a gameplay compatibility test."""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import io
import json
import re
import struct
import zipfile

from surface_motion import GAME, ROOT, tokens
from vpk import read_vpk

CAMPAIGN_MAP = re.compile(r'd[123]_(?:trainstation|canals|eli|town|coast|prison|c17|citadel|breen)_\d+[ab]?$')


def campaign_maps(game=GAME):
    """Installed original-HL2 campaign maps; exclude camera/background/test maps."""
    return sorted(p.stem for p in (game / 'maps').glob('*.bsp') if CAMPAIGN_MAP.fullmatch(p.stem))


def effects(body):
    values = words(body)
    found = []
    if '$xen_shift' in values:
        found.append('texture_motion')
    if 'xenesthesia/prism' in values:
        found.append('flowing_colour')
    if 'xenesthesia/weave' in values:
        found.append('rug_weave')
    if '$xen_sign_shift' in values:
        found.append('sign_echo')
    if not found:
        found.append('special_material_effect')
    return found


def lump(data, index):
    # Valve Source SDK 2013 src/public/bspfile.h: header and lump table.
    if data[:4] != b'VBSP' or struct.unpack_from('<i', data, 4)[0] not in (19, 20):
        raise ValueError('Unsupported BSP header')
    offset, size, version, compressed = struct.unpack_from('<4i', data, 8 + 16 * index)
    if compressed or min(offset, size) < 0 or offset + size > len(data):
        raise ValueError('Compressed or invalid BSP lump; do not infer coverage')
    return data[offset:offset + size]


def words(body):
    return [m[0].strip('"').lower() for m in tokens(body.decode('utf8'))]


def inventory():
    stock, read_stock = read_vpk(GAME / 'hl2_misc_dir.vpk')
    shipped, read_shipped = read_vpk(ROOT / 'content.vpk')
    generated = set(json.loads((ROOT / 'artifacts/surface-materials.json').read_text()))
    if not generated.issubset(shipped):
        raise ValueError('Generated material inventory differs from the package')
    report = {'runtime_sha256': hashlib.sha256((ROOT / 'content.vpk').read_bytes()).hexdigest(),
              'scope': 'Static material references only; excludes visibility, model usage and gameplay behaviour.',
              'viewmodels': {}, 'maps': {}, 'unreadable_maps': {}}
    effect_cache = {name: effects(read_shipped(name)) for name in generated}
    groups = defaultdict(list)
    for name in sorted(stock):
        if name.startswith('materials/models/weapons/v_') and name.endswith('.vmt'):
            groups[name.split('/')[3]].append(name)
    for group, names in groups.items():
        excluded = {}
        for name in names:
            if name in generated:
                continue
            values = words(read_stock(name))
            reasons = sorted(set(values) & {'$alphatest', '$translucent', '$additive',
                            '$decal', 'proxies', '$basetexturetransform'})
            excluded[name] = reasons or [f'unsupported shader or material: {values[0]}']
        report['viewmodels'][group] = {'included': len(names) - len(excluded),
                                      'total_definitions': len(names), 'excluded': excluded}

    uncovered = defaultdict(set)
    detailed_effects = {}
    for map_name in campaign_maps():
        data = (GAME / 'maps' / (map_name + '.bsp')).read_bytes()
        if not data:
            report['unreadable_maps'][map_name] = 'Empty installed BSP placeholder; no material table to audit.'
            continue
        strings, table = lump(data, 43), lump(data, 44)
        if len(table) % 4:
            raise ValueError('Invalid texture-name table')
        names = set()
        for (offset,) in struct.iter_unpack('<i', table):
            if not 0 <= offset < len(strings):
                raise ValueError('Texture-name offset out of bounds')
            name = strings[offset:strings.index(0, offset)].decode('utf8').lower().replace('\\', '/')
            names.add('materials/' + name + '.vmt')
        with zipfile.ZipFile(io.BytesIO(lump(data, 40))) as pak:
            local = {n.lower().replace('\\', '/'): pak.read(n) for n in pak.namelist()
                     if n.lower().endswith('.vmt')}

        def reference(name, seen=()):
            if name in seen or len(seen) > 12:
                return None
            if name not in local and name in generated:
                return name
            body = local.get(name)
            if body is None and name in stock:
                body = read_stock(name)
            if body is None:
                return None
            values = words(body)
            if not values or values[0] != 'patch' or 'include' not in values or 'proxies' in values:
                return None
            target = values[values.index('include') + 1].replace('\\', '/')
            return reference(target, seen + (name,))

        direct, inherited, material_effects, missing = [], {}, {}, {}
        for name in sorted(names):
            target = reference(name)
            if target == name:
                direct.append(name)
            elif target:
                inherited[name] = target
            if target:
                material_effects[name] = {'source': target, 'effects': effect_cache[target]}
            else:
                body = local.get(name)
                if body is None and name in stock:
                    body = read_stock(name)
                values = words(body) if body else []
                reasons = sorted(set(values) & {'$translucent', '$additive', '$decal',
                                'proxies', '$basetexturetransform', '$detail', '$seamless_scale'})
                missing[name] = {'shader': values[0] if values else 'missing', 'features': reasons}
                uncovered[name].add(map_name)
        authored_transforms = [name for name, body in local.items()
                               if name in inherited and any(v in words(body) for v in
                                  ('$basetexturetransform', '$bumptransform', '$bumptransform2'))]
        report['maps'][map_name] = {
            'bsp_sha256': hashlib.sha256(data).hexdigest(),
            'material_table_entries': len(names),
            'direct_overrides': len(direct),
            'patches_referencing_overrides': len(inherited),
            'other_materials': len(names) - len(direct) - len(inherited),
            'patch_sources': sorted(set(inherited.values())),
            'patches_with_authored_transforms': sorted(authored_transforms),
            'assigned_effect_counts': dict(Counter(effect for row in material_effects.values()
                                                   for effect in row['effects'])),
            'colour_only_sources': sorted({row['source'] for row in material_effects.values()
                                           if row['effects'] == ['flowing_colour']}),
            'uncovered_materials': missing,
        }
        detailed_effects[map_name] = material_effects
    report['campaign_map_count'] = len(report['maps'])
    report['uncovered_material_maps'] = {name: sorted(maps) for name, maps in sorted(uncovered.items())}
    target = ROOT / 'artifacts/coverage-audit.json'
    target.write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    detail_target = ROOT / 'artifacts/private/coverage-material-effects.json'
    detail_target.parent.mkdir(parents=True, exist_ok=True)
    detail_target.write_text(json.dumps(detailed_effects, indent=2) + '\n', encoding='utf8')
    print(target)
    for name, row in report['maps'].items():
        print(name, {key: value for key, value in row.items() if key not in
                    {'bsp_sha256', 'patch_sources', 'colour_only_sources', 'uncovered_materials'}})


if __name__ == '__main__':
    inventory()
