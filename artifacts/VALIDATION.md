# Playtest validation, 23 October 2026

## Initial colour-focused build (historical)

- Native Half-Life 2 Windows runtime, Anode session; no injected DLL, sv_cheats 0.
- Shader compilation and archive byte verification passed.
- Three package tests passed: exact archived content, compiled shader/native
  materials, and content-only package with opt-in key binding.
- Animated output inspected at 1280x720 and 1920x1080.
- Coast daylight and Ravenholm darkness/flashlight checked. Native HUD intact.
- Daylight on/off screenshots confirm the pistol and hands are included in the
  effect. Near-object distortion is intentionally gentler; dark gloves stay dark.
- F4 enabled/disabled the effect. Save/load in Ravenholm preserved working output.
- Short 657-frame coast demo at 1080p: 295.84 fps effect on, 311.37 fps bypassed.
  Single local runs, not a general performance guarantee or a full-game benchmark.
  Bypass also disables the replaced bloom/colour-correction passes.
- First live resolution-change attempt stayed at 720p; restarting at 1080p
  produced confirmed 1920x1080 screenshots. Both sizes were visually inspected.
- Native Workshop manager stopped responding in the isolated test harness.
  Its owned game process was closed and the test restarted. No upload was made.
- Publication and clean Workshop-download validation remain pending the owner's
  requested main-desktop playtest. No Workshop item has been created.

## Native installation correction

The first custom `-game` preview was not sufficient: after starting a chapter in
the menu, the anniversary runtime remounted subscribed ASCII content. Its episode
mounts also produced the wrong background and broken menu resources. These findings
supersede the earlier custom-harness installation claims.

The current preview uses the real installed `hl2_complete` game with
`hl2_expansion hl2`. Its native `path` output contains only base-HL2 campaign
assets and `hl2/custom/xenesthesia_playtest.vpk`; `hl2_episodic` reports 0.
ASCII is disabled in native `cfg/workshop.txt` (subscription retained).
`workshop_dump` shows no mounted Workshop addons. Original config/workshop files
were backed up to `artifacts/private/native-playtest-backup` before this change.
The runtime VPK was copied with a matching SHA-256. The preview now has working
native campaign menus and standard window borders. Publication remains on hold.

Native UI regression check passed: **Half-Life 2 > New Game > Highway 17** loaded
the original HL2 chapter with Xenesthesia visible, no ASCII rendering. F4 bypassed
and restored the shader; F6 opened the pause menu and released gameplay mouse input.

## Local surface-flow revision

- Removed the radial/crosshair field. Smoothed local colour and approximate depth
  now drive curling textures, spatial double edges and moving relief. Reduced
  palette mix from 0.58 to 0.24. No object IDs or geometry changes are claimed.
- Rejected an initial version whose full-resolution motion seeds made fine road
  textures too noisy. The retained version uses the existing blurred bloom buffer
  for the control field, preserving full-resolution detail in the final scene.
- Compiled successfully; all three package tests passed. The installed native VPK
  matches SHA-256 `1a41d9ba6f1b4f92dafc54d7ef66d8b93adda5995f4e619d43513878a0b66678`.
- Native 1280x720 Anode checks: coast road, railings, cliffs, pistol and hands;
  camera turn and forward movement; Ravenholm darkness and flashlight with SMG.
  Local motion remained visible while the HUD stayed sharp. Dark areas retain a
  gentler effect; object boundaries are approximate and can visibly bend.
- F4 bypass/restoration and F6 pause menu checked in Ravenholm. No ASCII output
  appeared during either native map load.
- A new native coast demo completed 2,610 benchmark frames: 410.05 fps with the
  effect requested on, 398.91 fps with bypass requested. These single 720p runs
  demonstrate successful real-time playback, not a reliable shader-cost estimate;
  run-to-run variation is larger than the measured difference. Bypass also disables
  normal bloom/colour correction. Restored the 120 fps cap afterwards.
- The old custom-harness demo was rejected by the native game-directory check;
  its accompanying frame report is invalid and excluded from these results.
- The previous 1080p measurements above describe the initial build only. This
  revision has been checked at 720p. Main-desktop subjective playtest and eventual
  clean Workshop-download validation remain pending. Nothing has been published.

## Material-coordinate revision (earlier, excessive-motion version)

User feedback rejected the surface-flow approximation: it still appeared attached
to the player and primarily produced blurry outlines. Those visual-quality claims
above are superseded. The current build animates supported materials directly.

- 1,917 native material overrides generated from installed original HL2. Original
  shader parameters and texture references retained; no texture images included.
- Native Sine/TextureTransform proxies animate scale, drift and rotation. Static
  props use a material phase. EntityRandom is restricted to weapon materials.
- First broad EntityRandom prototype exited during map startup. Inspection of
  Valve's implementation found an unchecked null entity for static renderables.
  Removing that proxy from static prop materials resolved both tested map loads.
- Corrected WorldVertexTransition to share the base texture transform, matching
  its shader definition. No generated-proxy initialization errors on the corrected
  Ravenholm/coast loads. Existing base-game material warnings remain.
- Stationary Ravenholm capture with post-process OFF proves texture interiors
  move: brick/window/concrete patterns change while the drainpipe, geometric wall
  outline and crosshair stay fixed. Eighteen native JPEG captures form the local
  4.5-second `material-motion/wall-motion.gif`; source frames are retained.
- Coast capture with post-process OFF proves road markings/cracks/rock details
  move with fixed scenery. Six native JPEG frames saved in `material-motion`.
  Pistol, hands and SMG included; forward movement and camera turns checked.
- All screen-space displacement, depth effects, blur and double edges removed.
  Current optional colour shader takes one unshifted full-frame sample. F4 checked
  off/on: colour changes while material motion continues. This is not full bypass.
- Nine package/generator tests passed. Full local disable/re-enable helpers tested
  with HL2 closed. Archive SHA-256:
  `e26da391e43b782425c3f62f30127069c2e371ceefefdceae446ccb8b2e178d9`.
- Final 720p native coast timedemo: 2,610 frames, 385.35 fps (2.60 ms/frame).
  One local run, not a full-game or minimum-performance guarantee. Restored 120 fps.
- Native tested scenes ran without further crashes. Broader campaign, 1080p and
  final Workshop-download checks remain pending. No Workshop upload or item exists.

## Subtle motion and restored prismatic colour (current)

The owner found the previous texture movement excessive and too regular, and
requested the missing kaleidoscopic colour effect. This revision addresses both.

- World material scale amplitude reduced from 6.5% to 0.12%, translation from
  4.5% to 0.35% of a texture repeat, and rotation from 1.8 to 0.006 degrees.
  World UVs can extend far beyond 0..1, so reducing scale/rotation was essential
  to avoid large sliding facades. Model limits: 0.6%, 0.3%, 0.12 degrees.
- Each parameter combines two bounded sine waves, weighted 65%/35%, with
  different periods. Base periods are 8–13 seconds, with slower axis variations.
  This gives gentler, less regular motion without unbounded texture drift.
- EntityRandom is now restricted to first-person weapon materials. World weapon
  models use the same safe material phase as other potentially static props.
- Restored prismatic hues and moving colour bands. The first revised colour
  prototype made fine asphalt grains overly colourful; using the native soft
  buffer only to drive hue resolved that speckling. Final detail comes from one
  sharp, unshifted full-frame sample. No spatial echoes or radial warp returned.
- Final shader compiled and all 10 package/generator tests passed. Native archive
  installation verified. SHA-256:
  `64c9cb296a7c2b7d50bd2769aeac887e39eb1d0afc8e85d00343b892375b5a40`.
- Native Anode 1920x1080: coast daylight, pistol/hands, Ravenholm darkness,
  flashlight, SMG, walking and camera turns checked. F4 bypass/restoration checked;
  F6 opened the pause menu. No generated-proxy errors or new crashes observed.
- Native coast timedemo: 2,610 frames in 7.741 seconds, 337.16 fps (2.97 ms/frame).
  This single local 1080p run is not a cost comparison with earlier 720p runs or
  a campaign-wide performance guarantee. Restored the 120 fps cap.
- Real 1080p screenshots retained in `subtle-motion`. Twelve stationary wall
  captures with the colour layer off preserve evidence of the reduced native UV
  animation. `wall-motion.mp4` is a 2 fps sequence of those timed screenshots,
  not a continuous gameplay recording. Older `material-motion` media shows the
  rejected excessive-motion build and must not represent the current release.
- Main-desktop subjective approval, final release media, broader campaign checks
  and eventual clean Workshop-download validation remain pending. No Workshop
  item has been created or uploaded.

## Local release preparation

- Created a separate illustrated cover, checked its title at thumbnail size, and
  retained the exact built-in image-generation prompt. The game gallery remains
  unretouched native captures from the current subtle-motion candidate.
- Exported 512x512 PNG/JPEG cover thumbnails. Both thumbnails and both selected
  screenshots are below 1,000,000 bytes. The full-resolution cover master is
  separate and is not the upload thumbnail.
- `tools/prepare-release.py` verified and staged all 1,925 runtime files from the
  tested VPK and checked the manual-install ZIP. Review materials are copied by
  explicit allowlist, excluding local saves, backups and the retired harness.
  This command has no Steam/API/upload operations.
- Local review copy, installation/removal instructions, listing text, licensing
  notice, media provenance and the publication handoff are included. They label
  F4 as colour-only, the cover as illustration, and the motion clip as a timed
  still-image inspection sequence. Publication remains subject to explicit approval.

## Static coverage audit while the main preview remains in use

- Read installed assets without changing the running game or its configuration.
  `tools/audit-coverage.py` records the exact runtime and sampled map hashes in
  `coverage-audit.json`; the readable summary is `release/COVERAGE.md`.
- All ten installed first-person hand material definitions are included. The
  RPG's main material is excluded because it uses alpha cutouts. The separate
  excluded SMG definition uses additive rendering and existing animation proxies.
  The listing now distinguishes texture-animation exclusions from colour coverage.
- Followed material-patch includes in nine chapter BSPs, from Trainstation through
  Breen/Citadel. Directly inspected inherited map patches contained no authored
  base/bump transforms that conflict with the new proxies. Reference counts are
  not visible-area percentages and do not prove runtime behaviour in those maps.
- Reviewed complete removal instructions and clarified that the local disable
  helper removes the preview VPK but leaves video preferences and F4/F6/F8 bindings
  for the owner to restore. No settings were changed during this audit.
