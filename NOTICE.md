# Attribution

The original Xenesthesia code, procedural colour/normal texture data, build tools and documentation are MIT licensed.
The packaging and native integration helpers derive from our City 17 ASCII
project, also MIT licensed: https://github.com/skulitom/city17-ascii

Half-Life 2, game assets and Valve trademarks belong to Valve. In-game screenshots
demonstrate the addon and are not covered by the MIT grant for our original code.
This is an independent addon and is not endorsed by Valve.

The Workshop thumbnail and gallery use genuine screenshots of the release build.
An earlier generated cover is retained only in development history; it is excluded
from this release and its listing.
The MIT grant applies to original code and documentation, not Valve assets,
screenshots or promotional art.

The generated world/prop/weapon/NPC .vmt files preserve material definitions from the
owner's installed Half-Life 2 and add our animation proxies. Those definitions,
including their copies inside content.vpk, are derived Valve game content and
are NOT licensed under our MIT grant. No Valve texture images or game binaries
are bundled. The original generator in tools/surface_motion.py is MIT licensed.
Generated material sources are excluded from Git and reproduced from the game
installation; artifacts/surface-materials.json records the source hashes.

Valve's ShaderCompile2 is fetched from the official Source SDK 2013 and checked
against its known SHA-256 before use. It is a development tool and is not shipped
in the runtime content or redistributed as part of the source release.

NPC deformation and continuous world colour compile twenty modified skin, eye, teeth, VortWarp, generic and lightmapped vertex shaders
from Valve's Source SDK, pinned by research/npc-sdk-files.json and research/surface-sdk-files.json. These compiled
.vcs files are Valve-derived SDK code, NOT MIT. The SDK's LICENSE and
thirdpartylegalnotices.txt are retained unmodified in third_party/valve-source-sdk
and included inside the VPK under xenesthesia/licenses. This addon must remain
free. Original patch/build code in tools/npc_pulse.py, tools/human_pulse.py, tools/surface_shaders.py and src/xen_*.h is MIT; the SDK license
continues to apply to the combined compiled shaders. Stock VortWarp and INTRO parameters 0..1 use the original vertex process. Classic NPC materials use warpparam >=2. Human skin/generic materials use a marked base transform to carry the pulse and entity origin; their original UVs are restored before sampling. Human deformation runs after native flex/skinning so CPU- and GPU-skinned pieces use the same entity-relative world field. Eyes/teeth use native INTRO parameters with the stock 0..1 behavior retained. Marked eye materials pass entity origin and pulse through EyeUp for the flashlight path; the regular eye lighting up-axis is reconstructed from iris projection V. Iris/glint projection still uses unwarped positions. Upright head/torso masking and broader cinematic compatibility remain release checks.

World colour uses an opt-in detail scale marker (-1337), decoded only by the modified lightmapped vertex paths. Only detail colour coordinates change; base texture, lightmap and bump coordinates retain their native paths. Unmarked shaders retain their original behavior. Movable models use texture-local colour.
