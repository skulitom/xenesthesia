# Campaign surface coverage — local preview

24 October 2026. Nothing created or uploaded on Workshop.

Runtime SHA-256: `0bb326b0b729c0b348af976e983ba5cc125c0a092fbf4e2df265d2795385beef`.
2,662 runtime files, 18,410,670 bytes, 2,632 generated material definitions.
Forty-two unit/package checks pass. No native shader or procedural texture
binary changed in this revision.

## Changes

- Added 68 definitions: legacy lab/industrial panels, composite building walls,
  storefronts, brush vehicle/train surfaces and translucent metal openwork.
- Added general UV motion to 37 existing metal cutouts. The general-motion
  total rises from 2,028 to 2,128; five of the new definitions keep their
  authored transform/animation and receive colour only.
- Architectural grates/stairs/rails/trusses/bars retain their original alpha
  test or transparency mode. Their complete base sample moves gently, so the
  holes and painted pattern stay aligned. This exception does not apply to
  glass, foliage, decals, faces or weapon cutouts.
- World translation amplitude rises from 0.0035 to 0.006 UV per axis (about
  three texels on a 512-texel texture). Scale and rotation bounds, two-wave
  timing, colour playback, NPC pulses and model motion strength are unchanged.
  The scalar rotation starts as a float to avoid integer math on its first bind.
- The static audit now enumerates all 68 non-empty original campaign maps.
  It records assigned effect counts, colour-only sources, inherited references
  and uncovered materials. The installed zero-byte d2_coast_02 placeholder is
  explicitly recorded. Camera, background and our fixture maps are excluded.

## Native validation in Anode

- `xen_coverage_lab` renders concretewall041a, alpha-tested metalgrate002a,
  translucent metalstair004a/004b, a legacy lab panel and a composite wall.
  Fixed-camera captures show changing mortar lines and grate patterns; holes
  remain visible, with no opaque filling or missing-material checkerboard.
- Reproduced the user's actual canals stairwell at position
  `-400 -7360 132`, angles `30 90 0`, in d1_canals_01. Its wall is
  concrete/concretewall041a, and its steps/landing use metalstair004a/004b.
  The paired `xen_canals_match_a/b.jpg` captures show motion of the texture
  itself as well as the colour field. A high-pass feature comparison on the
  wall puts the strongest integer match at roughly (-1, +3) image pixels;
  this is supporting image evidence, not a measurement of game-space motion.
- Checked the same stairwell with the flashlight. No missing native shader
  combo was logged. The architectural surfaces retain their native lighting.
- Checked a map-specific storefront reflection patch in d3_c17_13 at
  `4900 1150 70`, angles `0 90 0`. It inherits the new storefront animation;
  its windows, trim and reflection render normally in the paired captures.
- F5 restored stock materials in the test room and actual canals location,
  then returned to the mod. `xen_canals_stock_verified.jpg` is the verified
  OFF capture. All 2,632 prepared OFF files match their original installed
  material hashes.
- HUD/viewmodel visibility and cheat state were restored. The owned Anode
  game was closed, and the desktop lease was released. No campaign save was
  created.

## Test-harness interference and limits

One toggle overlapped the test harness reading the OFF files for hash checking.
Windows denied a directory move while those files were open; the companion
rolled back to ON and reported failure. After the read completed, the next
toggle succeeded. The incorrectly named intermediate `xen_canals_match_off`
capture is not included as OFF evidence. The private session log retains the
failure. No concurrent file scan is part of ordinary play.

The campaign audit is a static file/reference inventory, not a 68-map
playthrough or a promise that every visible material animates. Special shaders,
most glass/additive materials, authored animations and some embedded map
materials remain outside general UV motion. The fixture is brightly lit and
its captures are diagnostic, not listing media. No fresh performance benchmark
was run; no animation frames, harmonics or update rates were removed. Final
Workshop publication remains gated on the owner's explicit approval.
