# Barnacle/headcrab crash report — 25 October 2026

Status: **reported crash not reproduced; defensive candidate only.**
The Workshop release has not been updated by this investigation.

The [public report](https://steamcommunity.com/sharedfiles/filedetails/comments/3826155980)
states that d2_prison_07 crashes when a barnacle eats a headcrab. No error text,
save, platform, graphics configuration or other-addon list was supplied.

## Native checks

Windows original Half-Life 2, build 9912070, Direct3D 9; Anode session 3.
Both builds were mounted at startup with `-insert_search_path`; the Workshop
checkbox and City 17 ASCII remained disabled, with no loose material overrides.

| Check | Released build | Candidate |
| --- | --- | --- |
| Authored xen_barnacle_lab: grab, death attributed to barnacle, release | Survived | Survived, including 30-second marker |
| d2_prison_07 barnacle at 1999 -3662 -554 | Survived | Survived |
| d2_prison_07 barnacle at 2480 -3568 -554 | Survived | Survived |

The real map checks used noclip/notarget to observe, with a fresh classic
headcrab placed beneath each existing barnacle. The room's electrical
`trigger_hurt` was disabled during these controlled checks so it could not kill
the headcrab before the barnacle. One preliminary headcrab died to trigger_hurt
without a crash. The flashlight was used during the feeding checks. The console
recorded `Sending game message that npc_headcrab died to npc_barnacle` at both
locations for both builds. These checks do not reproduce the reporter's exact
save, route, timing or configuration.

`candidate-prison.jpg` is a genuine native screenshot from the second location.
Full console output and scratch comparison packages are kept privately outside
Git. The test map source is `tests/fixtures/xen_barnacle_lab.vmf`; it is not
included in the runtime addon.

## Candidate scope

Valve's [EntityRandom callback](https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/game/client/proxyplayer.cpp)
checks the incoming renderable but dereferences the result of BindArgToEntity
without checking whether it is null. A shared material can therefore be unsafe
on a renderable without a C_BaseEntity. This source-level hazard is established;
its involvement in the reported barnacle crash is **not** established.

The candidate removes EntityRandom from the two classic headcrab/zombie material
definitions and retains their existing time-driven sine clock. The 4.7-second
period, 0.04–0.75-unit expansion, original textures and compiled shaders are
unchanged. Instances now share a phase instead of a random per-entity offset.
No other NPC family, surface effect, shader binary or texture data changed.

- Released VPK SHA-256: `0bb326b0b729c0b348af976e983ba5cc125c0a092fbf4e2df265d2795385beef`.
- Candidate VPK SHA-256: `a405a187d120c1f0d2806143d9f770ccd76367a41a9fd043fb0144852911500b`.
- Byte comparison: same 2,662 archive paths; exactly two VMT bodies differ.
- All 43 automated checks passed, including the new callback regression guard.
- Both owned game processes were closed; the pre-test user configuration was restored.

## Still needed

A save just before the crash, exact error text or game crash dump, and confirmation
of the required launch option, operating system and other active addons. We need
a failing reproduction to establish causality and validate a fix for this report.
Do not describe the current candidate as a confirmed barnacle-crash fix or publish
it to Workshop on that basis.
