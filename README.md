# Xenesthesia

**Playtest build. Not published.** Workshop publication is held until the owner's
main-desktop playtest and approval. The Workshop text in `artifacts` is a draft.

On the author's prepared local machine, `tools/launch-playtest.ps1` opens the
isolated coast preview; `-Scene ravenholm` opens the saved night scene. F4 toggles
the effect and F5 quicksaves. This local harness is excluded from the release.

A native psychedelic shader for Half-Life 2's Windows 20th Anniversary edition.
Depth and light turn familiar surfaces into slowly flowing opalescent colour,
travelling contour bands and prismatic edge echoes. Menus, subtitles and the HUD
remain readable. The echoes are spatial colour offsets, not stored past frames.

## Install

Enable **Full HDR** under Options > Video > Advanced and use DirectX 9 with
Shader Model 2.b support. Disable City 17 ASCII and other post-processing material
overrides before enabling this addon. Only one of these filters can be active.

For a local install, put `content.vpk` into `Half-Life 2/hl2/custom/` under the name
`xenesthesia.vpk`, then restart. Remove that file and restart to uninstall.

For Workshop, subscribe, enable the addon in the game's Workshop menu, restart,
and start/load from the main menu. Direct `+map` startup can bypass Workshop mounting.

Optional developer-console commands:

```
exec xen_on
exec xen_off
exec xen_keys
```

`xen_keys` assigns F4 to toggle the filter and replaces any previous F4 binding.
It is never run automatically by the addon. `xen_off` bypasses the filter by
disabling bloom and colour correction for the session. Disable the addon and
restart to restore the original materials; use `xen_on` or your preferred video
settings to restore the post-processing passes. Reassign F4 in Controls or use
`unbind F4` to remove the optional binding.

## Compatibility

This is an original content-only VPK. It needs no ReShade, injected DLL or cheats.
It replaces `materials/dev/bloomadd.vmt` and `materials/dev/engine_post.vmt`, so it
conflicts with addons replacing either material. Normal bloom and colour grading
are replaced while the effect runs. The effect also affects the weapon viewmodel.

The scene-alpha depth cue is compressed and approximate. Sky, transparency and
water can behave differently. The shader uses this as an artistic cue; it does
not reconstruct world positions or change geometry, collision, AI or gameplay.
Custom maps/settings that suppress the post-process may suppress the effect.

## Build

Windows, Python 3.11+, and an installed Half-Life 2 are required for development.
The runtime package has no Python dependency.

```
powershell -File tools/bootstrap.ps1
python tools/build.py
python -m unittest discover -s tests -v
```

The build uses Valve's verified official shader compiler and the installed
game's VPK packer. Close the test game before rebuilding an archive it has mounted.
The build verifies archive bytes against the manifest, including detecting
packer failures that incorrectly return a successful process exit code.

`src` is the original shader, `content` is the Workshop upload root, `tools`
contains the build, and `testgame` is a local harness excluded from releases.

## License

Original source and documentation: MIT, see LICENSE. See NOTICE.md for Valve
assets, screenshots and development tools.
