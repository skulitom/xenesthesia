# Attribution

The original Xenesthesia code, procedural colour texture, build tools and documentation are MIT licensed.
The packaging and native integration helpers derive from our City 17 ASCII
project, also MIT licensed: https://github.com/skulitom/city17-ascii

Half-Life 2, game assets and Valve trademarks belong to Valve. In-game screenshots
demonstrate the addon and are not covered by the MIT grant for our original code.
This is an independent addon and is not endorsed by Valve.

The promotional cover is an AI-generated illustration made with the built-in
image-generation tool. It is labelled "ILLUSTRATED COVER" and is not an in-game
screenshot. Its prompt and provenance are in media/cover-prompt.txt in release
bundles, or artifacts/release/media/cover-prompt.txt in the source tree.
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

Experimental NPC deformation compiles fourteen modified skin, eye, teeth and VortWarp vertex shaders
from Valve's Source SDK, pinned by research/npc-sdk-files.json. These compiled
.vcs files are Valve-derived SDK code, NOT MIT. The SDK's LICENSE and
thirdpartylegalnotices.txt are retained unmodified in third_party/valve-source-sdk
and included inside the VPK under xenesthesia/licenses. This addon must remain
free. Original patch/build code in tools/npc_pulse.py, tools/human_pulse.py and src/xen_human_pulse.h is MIT; the SDK license
continues to apply to the combined compiled shaders. Stock VortWarp and INTRO parameters 0..1 use the original vertex process. Classic NPC materials use warpparam >=2; human skin uses a marked UV translation removed before base sampling. Human eyes/teeth use the same local deformation before skinning; eye projection uses the unwarped position. The eye flashlight path carries its marker in the otherwise unused EyeUp fourth component. Broader cinematic compatibility is a remaining release check.
