# Playtest validation, 23 October 2026

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
