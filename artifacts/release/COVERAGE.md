# Material coverage — revised preview

2,534 material definitions: 2,496 receive surface colour, 2,064 receive the full gentle UV animation, two classic zombie/headcrab materials use the original experimental geometry pulse, 125 humanoid definitions use coordinated head/upper-body expansion, and 15 additional creature definitions use normal-based expansion. Categories overlap.

All ten installed hand material definitions are included. The RPG cutout receives colour without moving its alpha silhouette. Authored animation blocks are preserved. Most transparent/additive materials and unsupported shaders (including UnlitTwoTexture screens) are excluded.

The human family counts are Alyx 8, Breen 5, Eli 5, citizens 83, Kleiner 8 and Mossman 6. Counts include separate eyes and mouth materials. Alyx and Kleiner were checked closely; Kleiner’s detached facial fragment is fixed, including the simpler lighting fallback. Not every family or cinematic has been visually tested. Five Combine soldier variants and five police/Barney definitions now carry the humanoid pulse. Fifteen definitions cover fast/poison zombies, additional headcrabs, antlions and the antlion guard; their native shading and cutout settings remain. Combine elite and antlion model phases and an actual metrocop were checked in a private native test room. Broader combat, ragdoll and cinematic coverage remains pending.

These are file/reference counts, not a percentage of visible scenery or a full-campaign compatibility claim. Map-specific patches can override inherited parameters. Native checks cover station walls, coast, Ravenholm and a private test room containing character models, a physics crate and computer monitors.

| Map | Direct material references | Patches referencing modified bases |
|---|---:|---:|
| d1_trainstation_01 | 90 | 107 |
| d1_trainstation_05 | 109 | 99 |
| d1_canals_01 | 108 | 155 |
| d1_canals_06 | 63 | 97 |
| d1_eli_01 | 91 | 53 |
| d1_town_01 | 69 | 272 |
| d2_coast_03 | 54 | 106 |
| d2_prison_01 | 45 | 104 |
| d3_c17_01 | 79 | 56 |
| d3_breen_01 | 13 | 359 |

World colour uses shared coordinates and timing across 1,401 compatible definitions, reducing texture-border colour cuts. Movable models retain local colour mapping. Special materials and lighting changes can still create visible borders.

Targeted lab additions: six standalone rug/decal materials use border-faded animated colour while preserving their base UVs and transparency. Four runner pieces use the shared world colour field; six carpet floors use normal colour and gentle UV motion. The two lab generator tubes share one Refract material with an original 16-second animated normal field; their authored orange tint texture and native silhouette/blur behavior remain. These are selective exceptions, not general support for every decal or glass surface.

The full two-wave motion is preserved. World materials share phase/period to reduce opposing motion at joins; arbitrary authored UV orientation/scale, base colours, special shaders and lighting boundaries can still reveal seams. An additional 120 opaque world definitions under props/ now receive compatible surface effects.
