# Xenesthesia

**Playtest build. Not published.** Workshop publication is held until the owner's
main-desktop playtest and approval. The Workshop text in `artifacts` is a draft.

On the author's local machine, `tools/install-playtest.ps1` installs the preview
in the normal game's `hl2/custom` folder, disables City 17 ASCII without
unsubscribing, backs up the original native settings, and selects original HL2.
`tools/launch-playtest.ps1` opens the native main menu in a bordered 1280x720 window.
Choose **Half-Life 2 > New Game** or load your usual HL2 save. F4 toggles only the
optional colour layer; texture motion stays active. F6 opens the pause menu to
release the mouse. To disable the complete local preview, close HL2 and run
`tools/disable-playtest.ps1`, then launch HL2 normally. The installer re-enables it.
The launcher also accepts `-Scene
coast` or `-Scene ravenholm` to enter those base-game maps directly. These preview
helpers and their settings are not included in the Workshop package.

The earlier custom `-game` harness is retired: the anniversary runtime remounts
content when switching campaigns, and that harness did not reproduce the native
menu and Workshop state correctly.

A native psychedelic material addon for Half-Life 2's Windows 20th Anniversary
edition. Brickwork breathes, floors drift and textures slowly stretch and rotate
on their surfaces. Motion happens in material coordinates before camera
projection, so it stays on the surface as you look around. Hands and weapons are
included, at a gentler strength. Geometry, the HUD and screen edges stay sharp.
An optional subtle colour layer adds a slow opalescent tint; it never blurs or
displaces the image. There are no screen-centred ripples or double-edge effects.

The current build animates 1,917 supported original HL2 materials. World surfaces
and props have timing derived from their material name; supported weapons also
use an entity phase. This is not independent animation of every object. Objects
sharing a material can move together. NPC faces, cutouts, transparent surfaces,
existing animated materials and special shaders are deliberately excluded.

## Install

For the optional colour layer, enable **Full HDR** under Options > Video > Advanced and use DirectX 9 with
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

`xen_keys` assigns F4 to toggle the colour layer and replaces any previous F4 binding.
It is never run automatically by the addon. `xen_off` bypasses only the colour
layer by disabling bloom and colour correction for the session. Texture motion
continues. **Disable the addon and restart for a full bypass.** Use `xen_on` or your preferred video
settings to restore the post-processing passes. Reassign F4 in Controls or use
`unbind F4` to remove the optional binding.

## Compatibility

This is an original content-only VPK. It needs no ReShade, injected DLL or cheats.
It replaces supported world/prop/weapon materials as well as
`materials/dev/bloomadd.vmt` and `materials/dev/engine_post.vmt`. It conflicts with
texture or material packs overriding those files. Normal bloom and colour grading
are replaced while the optional colour layer runs.

The material animation changes texture coordinates, not geometry, collision, AI
or gameplay. Painted-on windows, markings and other texture details move too;
material seams can become visible. Custom materials and untested episode content
are not guaranteed coverage. The optional colour pass is separate from texture
motion and no longer uses an approximate depth buffer.

## Build

Windows, Python 3.11+, and an installed Half-Life 2 are required for development.
The runtime package has no Python dependency.

```
powershell -File tools/bootstrap.ps1
python tools/build.py
python -m unittest discover -s tests -v
```

The build reads original material definitions from the installed game's
`hl2_misc_dir.vpk`, preserves their parameters, and adds native animation proxies
only to supported materials. Generated definitions are not original MIT assets.
It also uses Valve's verified official shader compiler and installed VPK packer.
Close the test game before rebuilding an archive it has mounted.
The build verifies archive bytes against the manifest, including detecting
packer failures that incorrectly return a successful process exit code.

`src` is the original shader, `content` is the Workshop upload root, `tools`
contains the build, and `testgame` is a local harness excluded from releases.

## License

Original source and documentation: MIT, see LICENSE. Generated material overrides
derive from Valve game definitions and are excluded from that grant. See NOTICE.md.
