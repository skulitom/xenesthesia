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

This preview mounts the package directly in an isolated game folder. It does not
change the user's City 17 ASCII Workshop subscription or overwrite their saves.
