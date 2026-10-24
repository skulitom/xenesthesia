"""Opt-in human pulse after native animation, anchored to the entity origin.

Marked base transforms transport pulse + origin to skin/generic vertex paths;
their UVs are restored before sampling. Eyes/teeth keep native shader families.
"""

FOLDERS = {'alyx', 'barney', 'kleiner', 'eli', 'mossman', 'breen', 'humans',
           'combine_soldier', 'police'}
# These creatures do not share the upright human head height. Inflate along
# their skinned normals instead, retaining native Phong, cutouts and lighting.
CREATURE_FOLDERS = {'zombie_fast', 'zombie_poison', 'headcrab', 'headcrab_black',
                    'antlion', 'antlion_guard'}
PICKUPS = {'materials/models/items/healthkit01.vmt',
           'materials/models/items/battery01.vmt',
           'materials/models/healthvial/healthvial.vmt'}
SHADERS = ('skin_vs20.fxc', 'Eyes_vs20.fxc', 'teeth_vs20.fxc', 'teeth_bump_vs20.fxc',
           'teeth_flashlight_vs20.fxc', 'eyes_flashlight_vs20.fxc')


def material(name, source, tokens):
    parts = name.split('/')
    if len(parts) < 4 or parts[1] != 'models' or (parts[2] not in FOLDERS | CREATURE_FOLDERS and name not in PICKUPS):
        return None
    if any(word in parts[-1] for word in ('emptool', 'glint', 'pupil')):
        return None
    ts = tokens(source)
    vals = [t[0].strip('"').lower() for t in ts]
    shader = vals[0]
    lens = name == 'materials/models/kleiner/glass2.vmt' and shader == 'unlitgeneric'
    if shader not in {'vertexlitgeneric', 'eyes', 'teeth'} and not lens:
        return None
    if any(key in vals for key in ('$basetexturetransform', '$warpparam', '$intro')):
        return None
    if '$additive' in vals and not lens:
        return None
    # Armoured enemies have no CPU-flexed face fragments. Select their head
    # from rest-pose height, then expand along skinned normals so the field
    # follows crouches and ragdolls instead of depending on world height.
    armoured = parts[2] == 'combine_soldier' or name == 'materials/models/police/metrocop_sheet.vmt'
    pickup = name in PICKUPS
    marker = 1003 if pickup else 1002 if armoured else 1001 if parts[2] in CREATURE_FOLDERS else 1000
    maximum = '.08' if armoured else '.16'
    # Antlion materials are shared by static gib models. EntityRandom is not
    # null-safe there. Origin is guarded by Valve's CEntityMaterialProxy; a
    # deterministic phase retains smooth animation on these shared materials.
    entity_phase = not pickup and parts[2] not in {'antlion', 'antlion_guard'}
    declarations = ['// Xenesthesia NPC pulse; all parts share the entity phase.',
                    '"$xen_hphase" "0"', '"$entityorigin" "[0 0 0]"']
    proxies = (['"EntityRandom" { "scale" "7" "resultVar" "$xen_hphase" }'] if entity_phase else [])
    proxies += ['"EntityOrigin" { }']
    if shader in {'vertexlitgeneric', 'unlitgeneric'}:
        # Preserve native alpha/lighting semantics. Both skin and generic
        # vertex paths understand the marker, including the glasses lenses.
        declarations += [f'"$xen_hshift" "[{marker} 0]"', '"$xen_hcenter" "[0 0]"',
                         f'"$basetexturetransform" "center 0 0 scale 1 1 rotate 0 translate {marker} 0"']
        proxies += [f'"Sine" {{ "sinePeriod" "5.3" "sineMin" "{marker}.01" "sineMax" "{marker}{maximum}" "timeOffset" "$xen_hphase" "resultVar" "$xen_hshift[0]" }}',
                    '"LinearRamp" { "rate" "0" "initialValue" "$entityorigin[2]" "resultVar" "$xen_hshift[1]" }',
                    '"TextureTransform" { "centerVar" "$xen_hcenter" "scaleVar" "$entityorigin" "translateVar" "$xen_hshift" "resultVar" "$basetexturetransform" }']
    else:
        declarations += ['"$intro" "1"', '"$warpparam" "2.01"']
        proxies += ['"Sine" { "sinePeriod" "5.3" "sineMin" "2.01" "sineMax" "2.16" "timeOffset" "$xen_hphase" "resultVar" "$warpparam" }']
        if shader == 'eyes':
            # EyeUp is the one shared constant available to the flashlight
            # path. For marked eyes it carries entity origin + pulse. The
            # regular shader reconstructs its lighting up-axis from iris V.
            # CFloatInput parses source vector components; Equals does not.
            # Copy components individually, avoiding Equals' 3-float buffer.
            proxies += [f'"LinearRamp" {{ "rate" "0" "initialValue" "$entityorigin[{i}]" "resultVar" "$eyeup[{i}]" }}' for i in range(3)]
            proxies += ['"Equals" { "srcVar1" "$warpparam" "resultVar" "$eyeup[3]" }']
    insertions = [(ts[-1].start(), '\n'+'\n'.join(declarations)+'\n')]
    if 'proxies' in vals:
        start = vals.index('proxies')+1
        level = 0
        for i in range(start,len(ts)):
            level += (vals[i]=='{') - (vals[i]=='}')
            if level == 0:
                insertions.append((ts[i].start(),'\n'+'\n'.join(proxies)+'\n'))
                break
    else:
        insertions[0] = (insertions[0][0],insertions[0][1]+'"Proxies" {\n'+'\n'.join(proxies)+'\n}\n')
    for offset, addition in sorted(insertions,reverse=True):
        source = source[:offset]+addition+source[offset:]
    return source


def once(source, anchor, replacement):
    if source.count(anchor) != 1:
        raise ValueError(f'Human shader anchor changed: {anchor}')
    return source.replace(anchor, replacement, 1)


def patch_local_pulse(source):
    """Pickup scale precedes skinning; enemy head mask uses rest-pose height."""
    anchor = '\tfloat4 vPosition = v.vPos;'
    source = once(source, anchor, anchor + '''
    if (cBaseTexCoordTransform[0].w >= 1003.0 && cBaseTexCoordTransform[0].w < 1004.0)
        vPosition.xyz *= 1.0 + (cBaseTexCoordTransform[0].w - 1003.0);
''')
    return source


def patch_shader(name, source):
    source = once(source, 'VS_OUTPUT main(', '#include "xen_human_pulse.h"\n\nVS_OUTPUT main(')
    anchor = '\t// Transform into projection space'
    if name == 'skin_vs20.fxc':
        source = patch_local_pulse(source)
        extra = """
    float xenMarker = cBaseTexCoordTransform[0].w;
    bool xenHuman = xenMarker >= 1000.0 && xenMarker < 1004.0;
    float3 xenOrigin = float3(cBaseTexCoordTransform[0].x,
                             cBaseTexCoordTransform[1].y, cBaseTexCoordTransform[1].w);
    if (xenHuman && xenMarker < 1002.0) XenNpcPulseWorld(worldPos, worldNormal, xenOrigin, xenMarker);
    if (xenMarker >= 1002.0 && xenMarker < 1003.0)
        worldPos += worldNormal * (smoothstep(52.0, 61.0, v.vPos.z) * (xenMarker - 1002.0) * 6.0);
"""
        source = once(source, anchor, extra+anchor)
        for field, uv, transform in [('x', 'x', 'cBaseTexCoordTransform[0]'),
                                      ('y', 'y', 'cBaseTexCoordTransform[1]'),
                                      ('z', 'x', 'cDetailTexCoordTransform[0]'),
                                      ('w', 'y', 'cDetailTexCoordTransform[1]')]:
            old = f'o.baseTexCoord.{field} = dot( v.vTexCoord0, {transform} );'
            source = once(source, old, f'o.baseTexCoord.{field} = xenHuman ? v.vTexCoord0.{uv} : dot( v.vTexCoord0, {transform} );')
    elif name == 'eyes_flashlight_vs20.fxc':
        source = once(source, 'const float4 cLightPosition',
                      'const float4 xenEyeUp : register( SHADER_SPECIFIC_CONST_7 );\nconst float4 cLightPosition')
        source = once(source, anchor, """
    float3 xenProjectionPos = worldPos;
    if (xenEyeUp.w >= 2.0 && xenEyeUp.w < 3.0)
        XenHumanPulseWorld(worldPos, xenEyeUp.xyz, xenEyeUp.w - 2.0);
"""+anchor)
        source = source.replace('float4(worldPos, 1)', 'float4(xenProjectionPos, 1)')
    else:
        source = source.replace('\tWorldSpaceVertexProcess(', '\tif (g_Time < 2.0) WorldSpaceVertexProcess(')
        extra = """
#if INTRO
    if (g_Time >= 2.0 && g_Time < 3.0) XenHumanPulseWorld(worldPos, modelOrigin, g_Time - 2.0);
#endif
"""
        if name == 'Eyes_vs20.fxc':
            extra = '\n    float3 xenProjectionPos = worldPos;\n'+extra
            source = source.replace('worldNormal = worldPos - cEyeOrigin;', 'worldNormal = xenProjectionPos - cEyeOrigin;')
            source = source.replace('float4(worldPos, 1)', 'float4(xenProjectionPos, 1)')
            source = once(source, '\tfloat normalDotUp =', """
    float3 xenLightingUp = cHalfEyeballUp;
#if INTRO
    if (g_Time >= 2.0 && g_Time < 3.0)
        xenLightingUp = -normalize(cIrisProjectionV.xyz) * 0.5;
#endif
\tfloat normalDotUp =""")
            source = source.replace('dot( worldNormal, cHalfEyeballUp)', 'dot( worldNormal, xenLightingUp)')
            source = source.replace('normalDotUp * cHalfEyeballUp', 'normalDotUp * xenLightingUp')
        source = once(source, anchor, extra+anchor)
    return source
