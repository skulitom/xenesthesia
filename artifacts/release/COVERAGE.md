# Material coverage — revised preview

2,409 material definitions: 2,376 receive surface colour, 1,950 receive gentle UV motion, two classic zombie/headcrab materials use the experimental geometry pulse, and 115 human material definitions use coordinated head/upper-body expansion. Categories overlap. Two special detail layers retain their authored colour.

All ten installed hand material definitions are included. The RPG cutout receives colour without moving its alpha silhouette. Authored animation blocks are preserved. Most transparent/additive materials and unsupported shaders (including UnlitTwoTexture screens) are excluded.

The human family counts are Alyx 8, Breen 5, Eli 5, citizens 83, Kleiner 8 and Mossman 6. Counts include separate eyes and mouth materials. Alyx and Kleiner were checked closely; Kleiner’s detached facial fragment is fixed, including the simpler lighting fallback. Not every family or cinematic has been visually tested. Barney and Combine remain colour-only.

These are file/reference counts, not a percentage of visible scenery or a full-campaign compatibility claim. Map-specific patches can override inherited parameters. Native checks cover station walls, coast, Ravenholm and a private test room containing character models, a physics crate and computer monitors.

| Map | Direct material references | Patches referencing modified bases |
|---|---:|---:|
| d1_trainstation_01 | 81 | 107 |
| d1_trainstation_05 | 87 | 98 |
| d1_canals_01 | 103 | 151 |
| d1_canals_06 | 62 | 97 |
| d1_eli_01 | 79 | 50 |
| d1_town_01 | 67 | 272 |
| d2_coast_03 | 51 | 103 |
| d2_prison_01 | 43 | 104 |
| d3_c17_01 | 62 | 56 |
| d3_breen_01 | 11 | 359 |

World colour uses shared coordinates and timing across 1,281 compatible definitions, reducing texture-border colour cuts. Movable models retain local colour mapping. Special materials and lighting changes can still create visible borders.

Targeted lab additions: six standalone rug/decal materials use border-faded animated colour while preserving their base UVs and transparency. Four runner pieces use the shared world colour field; six carpet floors use normal colour and gentle UV motion. The two lab generator tubes share one Refract material with an original 16-second animated normal field; their authored orange tint texture and native silhouette/blur behavior remain. These are selective exceptions, not general support for every decal or glass surface.
