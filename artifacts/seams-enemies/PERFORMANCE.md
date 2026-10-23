# Full-quality frame-time investigation

Local preview, 23–24 October 2026. No Workshop upload. The animation was **not simplified**: all ten sine components, five summed channels, original amplitude bounds, texture frames and liquid/rug animation are retained. World materials share their motion clock to reduce independent movement at joins; movable props keep their own rhythms.

## What the measurements show

| Capture | Seconds | Average FPS | 99th-percentile frame time | Frames over 33.3 ms |
|---|---:|---:|---:|---:|
| Previous build, first observed canal sweep | 21.94 | 28.8 | 256.51 ms | 179 |
| Stock game, canal sweep | 21.97 | 294.4 | 4.92 ms | 0 |
| Previous build, later repeat canal sweeps | 41.98 | 279.5 | 8.61 ms | 9 |
| Revised full-quality build, canal sweeps | 41.96 | 293.4 | 5.06 ms | 0 |
| Revised full-quality build, lab sweeps | 41.97 | 294.9 | 4.05 ms | 0 |

The previous build can run quickly without changing its animation. This makes first-use preparation/caching a stronger lead than the steady cost of its sine calculations. **This is a hypothesis, not a measured attribution to the driver, shader compiler or filesystem. First-use stutters remain a release blocker.** Do not present the difference between the first and later runs as an optimization speedup.

The simplified-animation candidate was reverted before installation/testing. The revised build's new NPC shader paths and extra material coverage were tested with full animation. Its normal compiler optimization setting remains unchanged; a separate optimization-level-3 probe was not shipped.

## Conditions and limitations

- Original HL2, 1280×720 bordered window on Anode's separate Windows desktop. VSync off for measurement, 300 FPS cap, `mat_queue_mode -1`, HDR level 2, no MSAA. VSync was restored to 1 afterward; no threading/preload settings were changed persistently.
- Fixed locations, camera rotating at 18 degrees/second, with a three-second measurement delay. Exact commands/positions, raw-data hashes and complete summaries are in `frame-times.json`. Compressed CSVs retain the original PresentMon samples.
- These are camera sweeps, not a scripted combat/walking benchmark. No shader builds ran during the selected captures. Some initial captures included a screenshot observation. Background scheduling, scene state and cache state were not held identical.
- The Windows/driver shader cache was not deleted. "First observed" is not a guaranteed cold-cache test. The later runs benefit from earlier encounters. The 300 FPS cap also limits useful comparisons of steady-state throughput.
- Before the revised canal capture, `mat_reloadallmaterials` was tried. Shader counts showed no newly created shaders from the command; its effect on first-use stalls was not isolated. It is **not** shipped as a fix or added to the user's launch settings.
- The first train capture and stock train comparison remain in the raw data. The stock train capture ends near game shutdown and is not used for the headline comparison. Earlier captures taken in a menu or an invalid camera position were excluded entirely.
- These results do not establish performance on the main desktop, other hardware, 1080p, uncached campaign areas, combat or cinematics.

## Tooling and follow-up

Portable [Intel PresentMon 2.6.0](https://github.com/GameTechDev/PresentMon/releases/tag/v2.6.0), downloaded from its official release with a valid Intel Authenticode signature. Unique ETW session names filtered only the owned HL2 process; no elevation, service installation or driver/cache setting changes. Analysis: `tools/frame-times.py`.

Investigate first encounters while retaining full quality: distinguish asset loading from first GPU use, test a preparation/warm-up mechanism if the native content interface supports it, and measure a repeatable walking/combat route on both reported maps. A language rewrite of the offline Python generator would not change the generated animation's native runtime work. An external native helper would need its own measured purpose and distribution plan.

Native shader layout references: [Valve's VCS format header](https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/public/materialsystem/shader_vcs_version.h), [compiler provenance](https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/devtools/bin/ShaderCompile2_readme.txt). No shader-format repacking experiment is shipped.
