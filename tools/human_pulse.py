"""Opt-in human pulse without replacing the native skin pixel/lighting shader.

Skin receives the pulse through an explicitly marked base-UV transform. Its
translation is removed before sampling, so the actual face texture never slides.
Eyes/teeth use their native INTRO parameter. Stock unmarked paths stay intact.
"""
from pathlib import Path

FOLDERS = {'alyx', 'barney', 'kleiner', 'eli', 'mossman', 'breen', 'humans'}
SHADERS = ('skin_vs20.fxc', 'Eyes_vs20.fxc', 'teeth_vs20.fxc', 'teeth_bump_vs20.fxc',
           'teeth_flashlight_vs20.fxc', 'eyes_flashlight_vs20.fxc')


def material(name, source, tokens):
    parts = name.split('/')
    if len(parts) < 4 or parts[1] != 'models' or parts[2] not in FOLDERS:
        return None
    if any(word in parts[-1] for word in ('emptool', 'glint', 'pupil')):
        return None
    ts = tokens(source)
    vals = [t[0].strip('"').lower() for t in ts]
    shader = vals[0]
    if shader not in {'vertexlitgeneric', 'eyes', 'teeth'}:
        return None
    if any(key in vals for key in ('$basetexturetransform', '$warpparam', '$intro', '$additive')):
        return None
    declarations = ['// Xenesthesia human pulse; all parts share the entity phase.',
                    '"$xen_hphase" "0"', '"$xen_hpulse" "0"']
    proxies = ['"EntityRandom" { "scale" "7" "resultVar" "$xen_hphase" }']
    if shader == 'vertexlitgeneric':
        # The skin path supports an engine-provided flat normal when there is
        # no bump map. Avoid introducing shiny highlights to matte materials.
        if '$phong' not in vals:
            declarations += ['"$phong" "1"', '"$basemapalphaphongmask" "1"', '"$phongboost" "0"']
        elif vals[vals.index('$phong')+1] != '1':
            return None
        declarations += ['"$xen_hshift" "[1000 0]"',
                         '"$basetexturetransform" "center 0 0 scale 1 1 rotate 0 translate 1000 0"']
        proxies += ['"Sine" { "sinePeriod" "5.3" "sineMin" "1000.01" "sineMax" "1000.16" "timeOffset" "$xen_hphase" "resultVar" "$xen_hshift[0]" }',
                    '"TextureTransform" { "translateVar" "$xen_hshift" "resultVar" "$basetexturetransform" }']
    else:
        declarations += ['"$intro" "1"', '"$warpparam" "2.01"', '"$entityorigin" "[0 0 0]"']
        proxies += ['"Sine" { "sinePeriod" "5.3" "sineMin" "2.01" "sineMax" "2.16" "timeOffset" "$xen_hphase" "resultVar" "$warpparam" }']
        if shader == 'eyes':
            # EyeUp xyz belongs to the engine. Its otherwise unused fourth
            # component reaches both regular and flashlight vertex shaders.
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
    elif name == 'eyes_flashlight_vs20.fxc':
        source = source.replace('const float4 cLightPosition',
                                'const float4 xenEyeUp : register( SHADER_SPECIFIC_CONST_7 );\nconst float4 cLightPosition',1)
        source = source.replace('\t// Perform skinning', '''
    float3 xenProjectionPos;
    SkinPosition(g_bSkinning, vPosition, v.vBoneWeights, v.vBoneIndices, xenProjectionPos);
    if (xenEyeUp.w >= 2.0 && xenEyeUp.w < 3.0)
        XenHumanPulse(vPosition.xyz, xenEyeUp.w - 2.0);
\t// Perform skinning''',1)
        source = source.replace('dot( cIrisProjectionU,  float4(worldPos, 1) )',
                                'dot( cIrisProjectionU,  float4(xenProjectionPos, 1) )')
        source = source.replace('dot( cIrisProjectionV,  float4(worldPos, 1) )',
                                'dot( cIrisProjectionV,  float4(xenProjectionPos, 1) )')
    else:
        insertions[0] = (insertions[0][0],insertions[0][1]+'"Proxies" {\n'+'\n'.join(proxies)+'\n}\n')
    for offset, addition in sorted(insertions,reverse=True):
        source = source[:offset]+addition+source[offset:]
    return source


def patch_shader(name, source):
    if source.count('#include "') < 1:
        raise ValueError('Missing SDK include')
    source = source.replace('VS_OUTPUT main(', '#include "xen_human_pulse.h"\n\nVS_OUTPUT main(',1)
    if name == 'skin_vs20.fxc':
        anchor = '\t// Perform skinning'
        source = source.replace(anchor, '''
    float xenMarker = cBaseTexCoordTransform[0].w;
    bool xenHuman = xenMarker >= 1000.0 && xenMarker < 1001.0;
    if (xenHuman) XenHumanPulse(vPosition.xyz, xenMarker - 1000.0);
''' + anchor,1)
        anchor = '\to.baseTexCoord.x = dot( v.vTexCoord0, cBaseTexCoordTransform[0] );'
        if source.count(anchor) != 1:
            raise ValueError('Skin UV anchor changed')
        source = source.replace(anchor,anchor+'\n\tif (xenHuman) o.baseTexCoord.x -= xenMarker;')
    else:
        # Insert before the first skinning call, after morphing. Preserve stock
        # intro behavior, but our marker uses the same local-space field as skin.
        anchor = ('\t// Transform the position and dummy normal' if name == 'Eyes_vs20.fxc'
                  else '\t// Normalize the flexed normal' if name == 'teeth_vs20.fxc'
                  else '\t// Transform the position' if name == 'teeth_flashlight_vs20.fxc'
                  else '\t// Perform skinning')
        if source.count(anchor) != 1:
            raise ValueError(f'Human deformation anchor changed: {name}')
        extra = '''
#if INTRO
    if (g_Time >= 2.0 && g_Time < 3.0) XenHumanPulse(vPosition.xyz, g_Time - 2.0);
#endif
'''
        if name == 'Eyes_vs20.fxc':
            extra = '''
    float3 xenProjectionPos;
    SkinPosition(g_bSkinning, vPosition, v.vBoneWeights, v.vBoneIndices, xenProjectionPos);
''' + extra
        source = source.replace(anchor,extra+anchor,1)
        source = source.replace('\tWorldSpaceVertexProcess(', '\tif (g_Time < 2.0) WorldSpaceVertexProcess(')
        if name == 'Eyes_vs20.fxc':
            # Eye projection vectors are produced by the unwarped model. Sample
            # with its original position so pupils do not slide over the eye.
            source = source.replace('worldNormal = worldPos - cEyeOrigin;', 'worldNormal = xenProjectionPos - cEyeOrigin;')
            source = source.replace('float4(worldPos, 1)', 'float4(xenProjectionPos, 1)')
            anchor = '\tif (g_Time < 2.0) WorldSpaceVertexProcess( g_Time, modelOrigin, worldPos, dummy, dummy, dummy );'
            source = source.replace(anchor, anchor+'\n\tif (g_Time < 2.0) xenProjectionPos = worldPos;')
    return source
