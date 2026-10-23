# Xenesthesia research

23 October 2026.

The concept combines animated depth/light-driven colour, luminous contour bands,
and depth-guarded prismatic offsets in a native HL2 post-process. This is an
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
rectangle to full-frame coordinates. Its five scene samples share colour and
compressed depth. Sampling coordinates are bounded to half-texel texture edges;
depth discontinuities reduce distortion and colour bleeding across silhouettes.

Temporal afterimages would require a retained previous frame. This content-only
implementation instead uses spatial colour echoes and describes them accordingly.
