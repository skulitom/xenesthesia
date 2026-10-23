# Asset coverage audit — 23 October 2026

This is an inventory of installed files and references, not a full-campaign
playtest or a measurement of visible surface area. The native gameplay checks
remain the coast/Ravenholm checks recorded in VALIDATION.md.

## Hands and weapons

All 10 installed `v_hand` material definitions are present in the animated
package. Supported definitions also cover the pistol, revolver, crowbar,
shotgun, crossbow, pulse rifle, gravity gun, grenade and bugbait. These counts
describe files, not a claim that every weapon has been individually playtested.

The RPG's main texture uses `$alphatest`: its alpha channel defines cutouts.
It is intentionally excluded from UV animation, preserving that shape. It still
receives the optional colour effect. Two of three SMG definitions are included;
the separate excluded definition is additive and already has authored proxies.
Additional installed/development weapon definitions are recorded in the JSON
audit without claiming they all appear during the original campaign.

## Representative chapter material tables

Many maps use small local material patches to select reflection cubemaps. Those
patches refer to base materials that the addon changes. A direct filename match
alone would substantially undercount the relevant references.

| Map | Material-table entries | Direct overrides | Patches referencing overridden bases | Other references |
| --- | ---: | ---: | ---: | ---: |
| Trainstation 01 | 460 | 72 | 107 | 281 |
| Canals 01 | 304 | 93 | 151 | 60 |
| Canals 06 | 201 | 53 | 97 | 51 |
| Black Mesa East 01 | 194 | 70 | 50 | 74 |
| Ravenholm 01 | 379 | 61 | 272 | 46 |
| Coast 03 | 231 | 44 | 103 | 84 |
| Prison 01 | 181 | 37 | 104 | 40 |
| City 17 01 | 158 | 53 | 56 | 49 |
| Breen 01 | 447 | 7 | 359 | 81 |

These tables include utility, sky, invisible and other special materials; the
figures are not an animation coverage percentage. Patch references indicate
possible inherited behaviour, not verified runtime mounting or appearance.
No directly inspected inherited map patch contained its own base/bump transform
in these nine maps. The audit does not enumerate model materials used by each map.

Priorities for further Anode checks are Trainstation (dense detail), Canals
(water/transparency), Prison (interior lighting) and Breen/Citadel (many reflective
material patches). These should wait until the owner's main preview is closed.

The reproducible audit is `python tools/audit-coverage.py`. Its JSON output records
the runtime hash, map hashes, base material references and weapon exclusions.
The current runtime hash begins `64c9cb29`.

Map parsing follows Valve's public [BSP header definitions](https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/public/bspfile.h),
using the material-name table and embedded material definitions. No maps or game
assets are changed or copied into the release by this audit.
