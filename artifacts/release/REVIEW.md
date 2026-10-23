# Revised preview — awaiting playtest

No Workshop item has been created or uploaded. Do not publish until the owner explicitly approves the revised build.

The previous release candidate is superseded. The current build anchors world colour continuously across material borders and keeps movable objects’ colour in their UVs and preserves the approved gentle texture motion. Coverage includes additional props, screens and NPC materials. F4 is now help only; full removal requires a restart.

The lab revision adds colour flow inside supported rugs without moving their alpha edges, continuous colour on runner pieces, six carpet-floor materials, and slow refraction eddies in Kleiner's generator tubes. Targeted native carpet/tank checks passed in d1_trainstation_05; diagnostic captures are retained in artifacts/lab-materials. User feedback remains required before release approval.

Experimental geometry pulses now cover classic zombies/headcrabs and selected human families. Human skin, hair, eyes and teeth share a deformation field, with native skin lighting retained. Alyx and Kleiner have been checked in Anode; Kleiner’s detached facial fragment is fixed by deforming after native animation; broader character/cinematic compatibility and low-detail validation remains release work. Old screenshots and the 337 FPS result describe the previous postprocess build, not this revision. Current captures, a fresh performance benchmark and final playtest feedback must be recorded before this review is marked ready.

## Seams, enemies and performance revision

Full animation quality is retained. World clocks are synchronized and opaque floor/panel coverage is wider. Combine/police and additional creature pulses preserve their native material families. Thirty package/unit checks pass and all 20 vertex layouts match retail. Native enemy captures and frame-time records are in artifacts/seams-enemies. Warm camera sweeps on both reported maps had no frames over 33.3 ms, but first-observed canal stalls were substantial. Cache state was not controlled: this is not proof of a performance fix. First-use stalls, real gameplay feedback and final gallery/compatibility work remain release blockers. No upload authorization has been requested.
