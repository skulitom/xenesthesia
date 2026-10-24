"""Targeted close-up effects using the installed sign and charger textures.

No OCR or replacement lettering: signs have a moving double-print layer. The
base sample/alpha stay fixed, including decal borders and cutout silhouettes.
Original generator code: MIT. Generated definitions retain Valve provenance.
"""
import hashlib

STATIONS = {
    'materials/models/props_combine/health_charger001.vmt',
    'materials/models/props_combine/health_charger_glass.vmt',
    'materials/models/props_combine/suit_charger001_sheet.vmt',
}
MODEL_SIGNS = {
    'materials/models/props_c17/streetsigns_composite01.vmt',
    'materials/models/props_c17/streetsigns_composite02.vmt',
    'materials/models/props_junk/ravenholmsign_sheet.vmt',
    'materials/models/props_trainstation/tracksigns01a.vmt',
}


def is_sign(name):
    name = name.lower()
    return (name in MODEL_SIGNS
            or name.startswith(('materials/props/sign', 'materials/props/metalsign',
                                'materials/props/plasticexitsign',
                                'materials/decals/decalsign', 'materials/decals/decal_sign',
                                'materials/decals/decalshipsign'))
            and not name.startswith('materials/props/signicon'))


def append(source, ts, declarations, proxies):
    # Both opt-ins decline authored proxy blocks, so never create duplicates.
    at = ts[-1].start()
    addition = '\n' + '\n'.join(declarations) + '\n"Proxies"\n{\n'
    addition += '\n'.join(proxies) + '\n}\n'
    return source[:at] + addition + source[at:]


def sine(result, period, low, high, phase=0):
    return (f'"Sine" {{ "sinePeriod" "{period:.6f}" "sineMin" "{low:.6f}" '
            f'"sineMax" "{high:.6f}" "timeOffset" "{phase:.6f}" "resultVar" "{result}" }}')


def station_material(name, source, tokenize):
    if name.lower() not in STATIONS:
        return None
    ts = tokenize(source)
    vals = [t[0].strip('"').lower() for t in ts]
    if (vals[0] != 'vertexlitgeneric' or vals[-1] != '}'
            or any(v in vals for v in ('proxies', '$detail', '$basetexturetransform',
                                      '$selfillumtint', '$color2', '$bumpmap', '$phong'))):
        raise ValueError(f'Charger material changed; inspect before patching: {name}')
    glass = name.endswith('health_charger_glass.vmt')
    declarations = [
        '// Xenesthesia charger: shared clock keeps body, glass and moving parts together.',
        '"$detail" "xenesthesia/prism"', '"$detailframe" "0"',
        '"$detailblendmode" "0"', '"$detailblendfactor" "1"', '"$detailscale" "1"',
        '"$xen_station_center" "[0 0]"', '"$xen_station_shift" "[1003 0]"',
        '"$basetexturetransform" "center 0 0 scale 1 1 rotate 0 translate 1003 0"',
    ]
    # Reuse the native pre-skin pickup branch with a much smaller 0.4-4.5%
    # breath. Original UVs, alpha, charge-state animation and lighting survive.
    proxies = [
        '"AnimatedTexture" { "animatedTextureVar" "$detail" '
        '"animatedTextureFrameNumVar" "$detailframe" "animatedTextureFrameRate" "9.5" }',
        sine('$xen_station_shift[0]', 7.3, 1003.004, 1003.045),
        '"TextureTransform" { "centerVar" "$xen_station_center" '
        '"translateVar" "$xen_station_shift" "resultVar" "$basetexturetransform" }',
    ]
    # The illuminated charge panels bypass ordinary diffuse lighting. Tint
    # their native emission instead of stripping the self-illumination mask.
    tint = '$color2' if glass else '$selfillumtint'
    declarations.append(f'"{tint}" "[1 1 1]"')
    for i in range(3):
        proxies.append(sine(f'{tint}[{i}]', 10.6, .45 if glass else .3, 1.15, i*10.6/3))
    return append(source, ts, declarations, proxies)


def sign_material(name, source, tokenize):
    if not is_sign(name):
        return None
    ts = tokenize(source)
    vals = [t[0].strip('"').lower() for t in ts]
    if (len(vals) < 4 or vals[0] not in {'lightmappedgeneric', 'vertexlitgeneric'}
            or vals[1] != '{' or vals[-1] != '}' or vals.count('$basetexture') != 1
            or any(v in vals for v in ('proxies', '$detail', '$detailtexturetransform',
                                      '$basetexturetransform', '$bumpmap', '$seamless_scale',
                                      '$additive', '$phong'))):
        return None
    texture = ts[vals.index('$basetexture')+1][0].strip('"').replace('\\', '/')
    model = vals[0] == 'vertexlitgeneric'
    transform = '$detailtexturetransform' if model else '$basetexturetransform'
    seed = int.from_bytes(hashlib.sha256(name.lower().encode()).digest()[:4], 'little')
    phase = (seed % 1000) / 137.0
    declarations = [
        '// Xenesthesia sign echo: original lettering splits, drifts and resolves.',
        # Retail HL2 omits the mode-2 lightmapped decal pixel combo. MOD2X
        # with half tint gives a dark ink echo and preserves base alpha.
        f'"$detail" "{texture}"', '"$detailblendmode" "0"', '"$detailtint" "[.5 .5 .5]"',
        '"$detailblendfactor" "0.0"',
        f'"$detailscale" "{1 if model else -1338}"',
        f'"{transform}" "center .5 .5 scale 1 1 rotate 0 translate 0 0"',
        '"$xen_sign_center" "[.5 .5]"', '"$xen_sign_shift" "[0 0]"',
        '"$xen_sign_scale" "[1 1]"', '"$xen_sign_rotation" "0.0"',
        '"$xen_sign_a" "0.0"', '"$xen_sign_b" "0.0"',
    ]
    # Sine forces the destination to float before Clamp chooses its operation.
    # A plain integer zero followed by Clamp truncates every sub-unit blend to
    # zero in retail Source, silently suppressing the complete sign effect.
    proxies = [sine('$detailblendfactor', 11.7, -.4, .7, phase),
               '"Clamp" { "srcVar1" "$detailblendfactor" "min" "0" "max" ".7" '
               '"resultVar" "$detailblendfactor" }']
    # Two bounded waves avoid a conveyor-belt scroll. The echo, not the base
    # sign, receives this transform. Zero blend restores exact stock lettering.
    for target, amount, base, period in (
            ('$xen_sign_shift[0]', .022, 0, 6.7),
            ('$xen_sign_shift[1]', .012, 0, 9.1),
            ('$xen_sign_scale[0]', .016, 1, 10.3),
            ('$xen_sign_scale[1]', .022, 1, 12.7),
            ('$xen_sign_rotation', .45, 0, 14.1)):
        proxies += [sine('$xen_sign_a', period, base-amount*.65, base+amount*.65, phase),
                    sine('$xen_sign_b', period*1.61803399, -amount*.35, amount*.35, phase),
                    f'"Add" {{ "srcVar1" "$xen_sign_a" "srcVar2" "$xen_sign_b" "resultVar" "{target}" }}']
    proxies += [f'"TextureTransform" {{ "centerVar" "$xen_sign_center" '
                '"scaleVar" "$xen_sign_scale" "translateVar" "$xen_sign_shift" '
                f'"rotateVar" "$xen_sign_rotation" "resultVar" "{transform}" }}']
    return append(source, ts, declarations, proxies)
