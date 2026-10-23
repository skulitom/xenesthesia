"""Read-only asset coverage inventory; this is not a gameplay compatibility test."""
from collections import defaultdict
from pathlib import Path
import hashlib
import io
import json
import struct
import zipfile

from surface_motion import GAME, ROOT, tokens
from vpk import read_vpk

MAPS = ['d1_trainstation_01', 'd1_trainstation_05', 'd1_canals_01', 'd1_canals_06', 'd1_eli_01',
        'd1_town_01', 'd2_coast_03', 'd2_prison_01', 'd3_c17_01', 'd3_breen_01']


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
    shipped, _ = read_vpk(ROOT / 'content.vpk')
    generated = set(json.loads((ROOT / 'artifacts/surface-materials.json').read_text()))
    if not generated.issubset(shipped):
        raise ValueError('Generated material inventory differs from the package')
    report = {'runtime_sha256': hashlib.sha256((ROOT / 'content.vpk').read_bytes()).hexdigest(),
              'scope': 'Static material references only; excludes visibility, model usage and gameplay behaviour.',
              'viewmodels': {}, 'maps': {}}
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

    for map_name in MAPS:
        data = (GAME / 'maps' / (map_name + '.bsp')).read_bytes()
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

        direct, inherited = [], {}
        for name in sorted(names):
            target = reference(name)
            if target == name:
                direct.append(name)
            elif target:
                inherited[name] = target
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
        }
    target = ROOT / 'artifacts/coverage-audit.json'
    target.write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(target)
    for name, row in report['maps'].items():
        print(name, {key: value for key, value in row.items() if key not in {'bsp_sha256', 'patch_sources'}})


if __name__ == '__main__':
    inventory()
