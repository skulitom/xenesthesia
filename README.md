# Xenesthesia

**Local playtest. Nothing uploaded to Workshop.** Publication requires the owner's explicit approval after playing the preview.

A native psychedelic material addon for the original Windows Half-Life 2 20th Anniversary edition. Gentle texture breathing and slowly unfolding prismatic colours live in surface coordinates, before camera projection. Walking or turning does not recenter the colour field on Gordon. The original textures, lighting, HUD and screen geometry remain readable.

The current material build covers 2,391 definitions. Compatible world surfaces, props, opaque NPC materials, cutouts, hands and weapons receive colour. The same subtle, two-wave UV motion approved in the previous preview remains on supported world/prop/weapon materials. NPC faces, cutouts and materials with authored animation receive colour without added UV movement. Standard grain detail layers are replaced by the original colour/grain field; special-purpose detail layers are preserved.

Colour shapes now bend and evolve in texture space, with different playback rates per material. Objects sharing a material can still animate together. This is not object recognition or independent animation of every item. Most transparent/additive materials, special shaders, UnlitTwoTexture displays and some map-specific overrides remain outside coverage. Classic zombies and classic headcrabs also have an experimental geometric pulse (up to 0.75 game units of surface-normal expansion). They keep their stock texture colours and use a different lighting shader; an experimental human head/upper-body pulse now covers 114 definitions for Alyx, Kleiner, Eli, Mossman, Breen and citizens. It preserves native skin lighting and deforms eyes/teeth with the head; Alyx has been checked closely, including flashlight rendering. Other character families still need full gameplay validation. Barney and Combine materials currently receive colour only. High shader detail with Phong and bump mapping enabled is required for this experimental human pulse; low-detail fallback remains release work.

## Local preview

`tools/install-playtest.ps1` installs the preview in native `hl2/custom`, disables City 17 ASCII without unsubscribing, backs up native settings, and selects original HL2. Run it only while HL2 is closed.

`tools/launch-playtest.ps1` opens the original game's menu in a bordered 1280×720 window. Start Half-Life 2 or load a normal save. F6 opens the pause menu and releases the mouse; F8 opens the console. F4 prints rollback guidance in the console.

**The old F4 colour toggle has been retired.** Colour now lives inside materials and cannot be disabled by switching off bloom. To disable all effects, close HL2, run `tools/disable-playtest.ps1`, then reopen HL2. The installer re-enables them. These helpers do not restore video preferences or F4/F6/F8 bindings; use Options for those. The original private backups are retained for reference.

## Manual installation

Put `content.vpk` in `Half-Life 2/hl2/custom/` as `xenesthesia.vpk`, then restart. Remove it and restart to uninstall. Use one Xenesthesia copy at a time. Disable other addons overriding the same materials, including City 17 ASCII. DirectX 9 is required; the new colour path has no custom HDR or bloom hook.

The addon never changes key bindings automatically. `exec xen_keys` opts into F4 help and restores normal game bloom/colour-correction settings previously changed by the old preview. `exec xen_off` explains removal; it no longer pretends to disable native material effects.

## Build and validate

Requires the locally installed original game and Python 3. The NPC build verifies and caches twelve pinned official SDK source files on first use. The build reads material definitions from that installation; it does not extract or redistribute Valve texture images.

```
powershell -File tools/bootstrap.ps1
python tools/build.py
python -m unittest discover -s tests -v
python tools/audit-coverage.py
```

`tools/human_pulse.py` coordinates human skin, hair, eyes and teeth deformation. Its native shader bytecode layouts are verified against the installed game. `tools/prism_texture.py` generates an original, mipmapped, 128-frame RGB colour field. `tools/surface_motion.py` augments supported VMTs while retaining existing animation blocks and protecting cutout UVs. `tools/build.py` packs the runtime content and verifies every archived byte. Source hashes and output hashes are recorded in `artifacts`.

`tools/prepare-release.py` stages an offline review package. It contains no upload calls. Workshop publication, a clean subscribed-install check and final screenshots remain gated on approval of the revised appearance. Earlier staged packages and their screenshots are superseded by the material-colour revision.

The old custom `-game` harness is retired; all current tests use the actual anniversary runtime. The previous postprocess shader source is retained for history, but neither its compiled shader nor its bloom/engine_post replacements ship.

## Licensing

Original code and procedural texture data: MIT. Valve-derived material definitions, compiled NPC shaders, game screenshots and promotional art are excluded from that grant. See NOTICE.md. This is an independent addon, not endorsed by Valve.
