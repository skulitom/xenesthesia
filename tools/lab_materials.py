"""Narrow opt-ins for carpet overlays and Kleiner's refracting generator tubes.

Original generator code: MIT. Generated VMTs retain their Valve provenance.
"""

RUGS = {'materials/overlays/rug001a.vmt'} | {
    f'materials/decals/decalrug00{i}a.vmt' for i in range(1, 6)}
RUNNERS = {f'materials/overlays/redrunner001{suffix}.vmt' for suffix in 'abcd'}
CARPET_FLOORS = {f'materials/props/carpetfloor00{i}a.vmt' for i in (1, 3, 4, 6, 7, 8)}
TANK = 'materials/models/props_lab/tank_glass001.vmt'


def tank_material(name, source, tokenize):
    if name.lower() != TANK:
        return None
    ts = tokenize(source)
    words = [t[0].strip('"').lower() for t in ts]
    if words[0] != 'refract' or words[-1] != '}':
        raise ValueError('Generator tube shader changed; review its material before patching.')
    replacements = []
    root_keys = {}
    depth = 0
    for i, word in enumerate(words):
        if depth == 1 and word.startswith('$'):
            root_keys.setdefault(word, []).append(i+1)
        depth += (word == '{') - (word == '}')

    def replace_value(key, value):
        indices = root_keys.get(key, [])
        if len(indices) != 1:
            raise ValueError(f'Unexpected tank parameter count: {key}')
        t = ts[indices[0]]
        replacements.append((t.start(), t.end(), f'"{value}"'))

    replace_value('$normalmap', 'xenesthesia/eddy_normal')
    # The orange tint texture, model flag, silhouette fade, blur and DX60
    # fallback stay authored. A gentler refraction reveals the new slow eddies.
    replace_value('$refractamount', '.12')
    replace_value('$refracttint', '[1 .9 .72]')
    changed_animation = changed_scroll = 0
    for i, word in enumerate(words[:-1]):
        if word not in {'animatedtexture', 'texturescroll'} or words[i+1] != '{':
            continue
        end, depth = i+2, 1
        while depth:
            depth += (words[end] == '{') - (words[end] == '}')
            end += 1
        block = words[i+2:end-1]
        if word == 'animatedtexture' and '$normalmap' in block:
            frame = block.index('animatedtextureframerate') + i + 3
            replacements.append((ts[frame].start(), ts[frame].end(), '"16"'))
            changed_animation += 1
        if word == 'texturescroll' and '$bumptransform' in block:
            # Motion is now inside the normal map, without a conveyor-belt UV
            # scroll. The original tint texture also stops sliding on the glass.
            replacements.append((ts[i].start(), ts[end-1].end(),
                                 '// Xenesthesia: the eddy normal map animates in place.'))
            changed_scroll += 1
    if (changed_animation, changed_scroll) != (1, 1):
        raise ValueError('Generator tube proxy structure changed; refusing a partial patch.')
    for start, end, value in sorted(replacements, reverse=True):
        source = source[:start] + value + source[end:]
    return source
