# Xenesthesia

**Local playtest. Nothing uploaded to Workshop.** Publication requires the owner's explicit approval after playing the preview.

A native psychedelic material addon for the original Windows Half-Life 2 20th Anniversary edition. Gentle texture breathing and slowly unfolding prismatic colours live in surface coordinates, before camera projection. Walking or turning does not recenter the colour field on Gordon. The original textures, lighting, HUD and screen geometry remain readable.

The current material build covers 2,564 definitions. Compatible world surfaces, props, opaque NPC materials, cutouts, hands and weapons receive colour. The complete two-wave UV animation is retained on supported world/prop/weapon materials. Connected world materials now share the same motion clock; props and weapons retain their individual rhythms. NPC faces, cutouts and materials with authored animation receive colour without added UV movement. Standard grain detail layers are replaced by the original colour/grain field; special-purpose detail layers are preserved.

Colour shapes bend and evolve over time. Connected world surfaces use a continuous world-space field and shared clock to reduce colour seams at texture borders. Movable objects keep UV-local patterns and per-material playback rates. Objects sharing a material can still animate together. This is not object recognition or independent animation of every item. Six rug overlays now have a dedicated, border-faded colour flow; four runner pieces share world colour, and six carpet-floor materials receive the standard gentle motion. Kleiner’s generator tubes use an original, slowly evolving normal map for liquid distortion, retaining their orange tint texture and native glass rendering. Most other transparent/additive materials, special shaders, UnlitTwoTexture displays and some map-specific overrides remain outside coverage. Classic zombies and classic headcrabs also have an experimental geometric pulse (up to 0.75 game units of surface-normal expansion). They keep their stock texture colours and use a different lighting shader; an experimental human head/upper-body pulse now covers 119 humanoid definitions for Alyx, Kleiner, Eli, Mossman, Breen, citizens and police/Barney. It preserves native skin lighting and deforms the complete rendered character after native animation, including eyes, teeth and Kleiner’s glasses. Alyx and Kleiner have been checked closely; the detached facial fragment is fixed in this preview. Other character families still need full gameplay validation. Six armoured Combine/metrocop materials now use a much subtler head pulse selected from model coordinates, so it follows ragdoll poses. Barney retains the coordinated humanoid pulse. Health kits, health vials and suit batteries have a gentle 1–16% shape breath alongside animated colour; their markings and native glow remain. Fast/poison zombies, additional headcrabs and antlions use a normal-based body pulse that preserves their native shaders and alpha masks. The human pulse preserves each material’s original Phong, alpha and transparency settings, with both skin and generic vertex paths. Full low-detail and cinematic regression remains release work.

Close-up additions: the wall health and suit chargers have coordinated 0.4–4.5% breathing, flowing colour across their glass/body and cycling illumination. Sixty-seven sign definitions use a drifting ink echo that periodically clears. This reuses the installed sign image; it does not recognize or replace individual letters. The base UV and alpha silhouette stay fixed. Authored sign animations and special shaders are excluded.

Performance investigation: individual frame times now distinguish first-observed passes from repeat passes. The largest stalls were concentrated in first-use conditions; warm runs with the full animation are fast. Shader/asset preparation is a working hypothesis, not a proven root cause or a resolved release issue. See `artifacts/seams-enemies/PERFORMANCE.md`.

## Local preview

`tools/install-playtest.ps1` installs the preview in native `hl2/custom`, disables City 17 ASCII without unsubscribing, backs up native settings, and selects original HL2. Run it only while HL2 is closed.

`tools/launch-playtest.ps1` opens the original game's menu in a bordered 1280×720 window and starts the optional local F5 companion. Start Half-Life 2 or load a normal save. **F5 switches every mod material off/on**, with a brief material refresh. F6 opens the pause menu and releases the mouse; F8 opens the console. F4 prints help. F5 replaces the preview's former screenshot binding; the original config backup is retained.

F5 uses an optional Windows companion built from `tools/live_toggle.cs` using the installed .NET Framework compiler. It changes only prepared, owned material directories and uses native console commands to refresh them. It does not inject code, read game memory or process animation frames. The OFF copies are byte-for-byte originals from the installed game. On exit it removes its loose material overrides, so ordinary launches and addon removal work normally. A standalone Workshop VPK cannot run this companion: the live toggle currently belongs to the local preview launcher, and its eventual optional distribution remains release work.

For complete removal, close HL2, run `tools/disable-playtest.ps1`, then reopen HL2. The installer re-enables the preview. These helpers do not restore video preferences or F4/F5/F6/F8 bindings; use Options for those. The original private backups are retained for reference.

## Manual installation

Put `content.vpk` in `Half-Life 2/hl2/custom/` as `xenesthesia.vpk`, then restart. Remove it and restart to uninstall. Use one Xenesthesia copy at a time. Disable other addons overriding the same materials, including City 17 ASCII. DirectX 9 is required; the new colour path has no custom HDR or bloom hook.

The addon never changes key bindings automatically. `exec xen_keys` opts into F4 help and the companion's F5 toggle, and restores normal game bloom/colour-correction settings previously changed by the old preview. Without the companion, F5 explains the launcher requirement. `exec xen_off` explains switching/removal.

## Build and validate

Requires the locally installed original game and Python 3. The build verifies and caches pinned official SDK sources for NPC and world vertex shaders on first use (see research/*-sdk-files.json). The build reads material definitions from that installation; it does not extract or redistribute Valve texture images.

```
powershell -File tools/bootstrap.ps1
python tools/build.py
python -m unittest discover -s tests -v
python tools/audit-coverage.py
```

`tools/human_pulse.py` coordinates human skin, hair, eyes, teeth and Kleiner’s glasses deformation. `tools/surface_shaders.py` preserves generic material shading and gives world colour a continuous coordinate field. Its native shader bytecode layouts are verified against the installed game. `tools/prism_texture.py` generates an original, mipmapped, 128-frame RGB colour field. `tools/lab_textures.py` adds the rug colour field and a 256-frame liquid normal map; `tools/lab_materials.py` limits special-material changes to explicit names. `tools/surface_motion.py` augments supported VMTs while retaining existing animation blocks and protecting cutout UVs. `tools/build.py` packs the runtime content and verifies every archived byte. Source hashes and output hashes are recorded in `artifacts`.

`tools/prepare-release.py` stages an offline review package. It contains no upload calls. Workshop publication, a clean subscribed-install check and final screenshots remain gated on approval of the revised appearance. Earlier staged packages and their screenshots are superseded by the material-colour revision.

The old custom `-game` harness is retired; all current tests use the actual anniversary runtime. The previous postprocess shader source is retained for history, but neither its compiled shader nor its bloom/engine_post replacements ship.

## Licensing

Original code and procedural texture data: MIT. Valve-derived material definitions, compiled shaders, game screenshots and promotional art are excluded from that grant. See NOTICE.md. This is an independent addon, not endorsed by Valve.
