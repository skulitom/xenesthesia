# Chargers and drifting sign lettering — local preview

24 October 2026. Nothing uploaded to Workshop. Runtime SHA-256:
`10e1f3ecea1633ce189cbd2a967cf104fa9cfd83a1fc4ca66985e3d288f157d2`.
2,594 files, 18,172,283 bytes; 2,564 generated material definitions. Forty
unit/package checks pass. Native vertex combo layouts remain compatible.

## Changes

- The health charger's body and glass and the suit charger's sheet share a
  0.4–4.5% shape breath, 7.3-second period and flowing prismatic detail. The
  illuminated panels receive a separate slow RGB tint. Their original emission
  masks, glass transparency, textures and native charging animations remain.
- Sixty-seven sign definitions receive a drifting ink echo. It uses the same
  installed image a second time, with two slow waves per transform channel and
  a fade that reaches zero regularly. This is not OCR or literal letter
  substitution. Base UVs and base alpha remain fixed. Lightmapped signs use
  detailscale -1338 to route their animated transform to detail only; native
  model signs use their independent detail transform.
- The two world vertex shaders gained the selective sign path, including the
  flashlight path. All general world/prop animation quality and the latest
  gentle Combine pulse remain unchanged. No texture images or texture frames
  were added. The archive grew by 108,547 bytes from the preceding preview.

## Native checks in Anode

- Both real charger entities rendered at close range. Health rose from 70 to
  100 while using the health charger; suit armour rose from 0 to 48 during the
  armour charger check. Animated gauge/glass and panel shading remained intact.
- Warning decals, including the exact ADMITTANCE TO AUTHORIZED PERSONNEL ONLY
  sign from the user's screenshot, showed changing lettering at a fixed camera.
  An opaque WARNING / NO TRESPASSING board also rendered. Flashlight toggles did
  not produce a missing shader combo or displaced decal silhouette.
- Fixed-camera native samples demonstrate both distorted and clear lettering.
  `xen_sign_final_*` captures are from the corrected local-material probe;
  `xen_warning_flashlight*` and `xen_warning_off_final` are from the final VPK.
- F5 restored the stock appearance and returned to the mod. All 2,564 prepared
  OFF material files were checked against original installed hashes. Exit while
  OFF cleaned up the loose material mount before the main preview was launched.
- Restored HUD/viewmodel settings and sv_cheats 0; no campaign save was made.
  The owned Anode game was closed and the desktop lease released.

## Issues found and resolved

The first sign candidate requested detail blend mode 2, which retail HL2 omits
from its lightmapped pixel shader combos. The final build uses supported MOD2X
with half tint for a dark ink echo; base alpha remains unchanged. The second
candidate's fade stayed at zero because Source's Clamp preserves an integer
destination type. Sine now writes directly to the destination first, forcing a
float before the clamp. Native samples confirmed that the fade then animates.

A diagnostic console command printed an unterminated line, joining the F5
request to that output and causing a timeout. The companion now emits a blank
line before its exact request marker. The original failure was reproduced, and
the corrected request toggled successfully after the same unterminated output.
The generated-script regression check is included in the passing suite.

## Limits

These are diagnostic screenshots, not approved Workshop listing media. Full
campaign coverage, model-sign variants, other graphics settings and a fresh
frame-time benchmark remain release work. A model-sign fixture did not produce
a reliable close-up and is not counted as visual validation; its attempted
spawn diagnostics are retained in the private session log. No claim is made
that every text-bearing texture is recognized. Publication still requires the
user's explicit go-ahead.
