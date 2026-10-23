# Attribution

The original Xenesthesia shader, build tools and documentation are MIT licensed.
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

The generated world/prop/weapon .vmt files preserve material definitions from the
owner's installed Half-Life 2 and add our animation proxies. Those definitions,
including their copies inside content.vpk, are derived Valve game content and
are NOT licensed under our MIT grant. No Valve texture images or game binaries
are bundled. The original generator in tools/surface_motion.py is MIT licensed.
Generated material sources are excluded from Git and reproduced from the game
installation; artifacts/surface-materials.json records the source hashes.

Valve's ShaderCompile2 is fetched from the official Source SDK 2013 and checked
against its known SHA-256 before use. It is a development tool and is not shipped
in the runtime content or redistributed as part of the source release.
