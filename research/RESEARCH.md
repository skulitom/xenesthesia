# Xenesthesia research

23 October 2026.

## Current approach: native material animation

User testing rejected the screen-space approximation below: it still felt tied
to the player and emphasized blurry outlines instead of moving texture interiors.
The current build uses native Sine and TextureTransform material proxies to
animate scale, translation and rotation before the camera projects a surface.
World/prop phases are deterministic per material; weapons also use EntityRandom.
Static props must not use EntityRandom: the public implementation dereferences
BindArgToEntity without testing the returned pointer. That prototype crashed;
removing the entity-only proxy from static props resolved the tested crashes.

WorldVertexTransition shares BASETEXTURETRANSFORM for its two base layers; there
is no separate $basetexturetransform2 in this runtime. Bump transforms are kept in
step. Existing proxies/transforms, transparent and cutout materials are skipped.
The generator currently produces 1,917 material overrides from installed HL2,
retaining Valve parameters and texture references. No texture images are copied.

The current post-process uses one unshifted full-frame sample for sharp detail
and one native blurred-buffer sample to drive broad prismatic colour regions.
The compressed scene-alpha depth cue influences hue only. All screen-space
displacement and double edges were removed. F4 controls that colour layer only. Material animation needs addon
disable/restart for a complete bypass; the installed client exposes no generic
ConVar-reading material proxy to support a native global on/off switch here.

Primary implementation references:
- https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/game/client/matrixproxy.cpp
- https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/game/client/mathproxy.cpp
- https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/game/client/proxyplayer.cpp
- https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/materialsystem/stdshaders/worldvertextransition.cpp

## Earlier screen-space prototypes (superseded)

The concept combines local liquid distortion, moving relief, luminous contour
bands, and depth-guarded double edges in a native HL2 post-process. This is an
independent shader; there is no third-party shader code in the package.

Initial web searches for HL2 psychedelic/hallucinogenic shaders found older
dream/psychedelic projects, including the archived L.S.D. (Lucid Source Dreaming)
project: https://www.moddb.com/mods/lsd/. No matching native combination was
identified in that search. This is not proof of uniqueness or an exhaustive audit.

Native integration builds on the tested City 17 ASCII pipeline. Valve's public
ScreenSpace General shader accepts original compiled shaders and material
constants. The CurrentTime material proxy supplies game time without a binary
plugin. The shipped HL2 client was checked for that registered proxy, and its
animation was verified in the game.

References:
- https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/materialsystem/stdshaders/screenspace_general.cpp
- https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/game/client/timematerialproxy.cpp
- https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/game/client/viewpostprocess.cpp

The shader inherits the corrected mapping from the quarter-resolution bloom
rectangle to full-frame coordinates. The current surface-flow revision uses
twelve texture samples: nine full-frame colour/depth samples and three samples
from the existing blurred bloom buffer. The blurred buffer drives motion only;
output detail comes from the full-resolution scene. This avoids using individual
fine texture grains as unrelated motion seeds. Sampling coordinates are bounded
to half-texel texture edges; depth discontinuities reduce distortion and colour
bleeding across silhouettes.

The previous crosshair-centred field is removed. Local colour, brightness and
depth determine phases and directions, with gradients bending motion around
surface features. This is an approximation, not per-object segmentation: this
native post-process supplies no object IDs, and the shader does not reconstruct
world coordinates. Similar objects can share motion, and camera movement changes
the sampled fields. Actual object deformation would need a different integration.

Temporal afterimages would require a retained previous frame. This content-only
implementation instead uses spatial colour echoes and describes them accordingly.
