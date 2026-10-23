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
