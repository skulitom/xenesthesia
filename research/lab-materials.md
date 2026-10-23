# Carpet and generator-tube revision

The supplied carpet is in d1_trainstation_05. Its material table contains overlays/rug001a and decals/decalrug002a. The two static generator-tube models use models/props_lab/tank_glass001, a Refract material. All source VMT bytes come from the owner’s installed game; their hashes are recorded in artifacts/surface-materials.json.

Targeting is explicit. Rug alpha and base UVs stay authored; only a new MOD2X detail colour layer animates. Its perimeter fades to neutral. This is flowing illumination/colour through the weave, not per-pixel geometric warping of the original carpet motif. Runner pieces share the existing world field to avoid colour jumps at joins. The generator material keeps its tint image, DX60 fallback, silhouette fade and blur. An original 256-frame normal map replaces its water normal and linear UV scroll, and distortion strength drops from .2 to .12. Both fields are computed from mathematics without copying game texture images.

Parameter and normal-sampling behavior checked against Valve’s pinned single-player SDK:
- [Refract material parameters](https://github.com/ValveSoftware/source-sdk-2013/blob/7309a5f13f63fdcc7b1e090f6c176113a9d95061/sp/src/materialsystem/stdshaders/refract.cpp)
- [Refract pixel shader](https://github.com/ValveSoftware/source-sdk-2013/blob/7309a5f13f63fdcc7b1e090f6c176113a9d95061/sp/src/materialsystem/stdshaders/refract_ps2x.fxc)
- [Native texture/constant setup](https://github.com/ValveSoftware/source-sdk-2013/blob/7309a5f13f63fdcc7b1e090f6c176113a9d95061/sp/src/materialsystem/stdshaders/refract_dx9_helper.cpp)

No new compiled shader paths are needed for these additions. Only the targeted materials and two original animated textures are added. Ordinary glass, decals, particles and UI remain excluded.
