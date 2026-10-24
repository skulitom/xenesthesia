# Inspection and live switching — 24 October 2026

Local original HL2 preview only. No Workshop upload.

- Final Combine/metrocop pulse: 0.06–0.48 Source units along skinned normals, selected using rest-pose head height. User rejected the first two stronger versions; this is the reduced third version.
- Actual health kit, health vial and suit battery inspected with colour and 1–16% geometry breathing. Native glow and labels remain.
- Inspected a prop ragdoll and an actual Combine soldier killed in the test room; the field stays with the posed head.
- F5 restored original appearance and enabled the mod again. All 2,534 OFF material files were independently hash-checked against the installed originals. Several subsequent OFF/ON cycles completed.
- Initial prototype nested exec polling caused a stack overflow. Replaced it with a bounded alias chain started by the key binding after exec returns; native retest passed. A diagnostic file-hash scan temporarily locked a directory during another toggle; the swap failed safely and a retry succeeded. Final companion adds short rename retries and clears stale failure replies.
- Companion cleanup verified after exiting while OFF: process exited and the mounted loose materials directory was removed. Original/mod copies remain in the owned staging folder for the next preview.
- 34 automated tests pass, including protocol, stale reply, exact byte restoration, swap failure, exit cleanup, material alpha/shading preservation and native shader layout checks. All 20 vertex-shader layouts match the retail ABI. No new frame-time benchmark was taken in this revision.

F5 needs the optional local Windows companion. It is not automatic in the standalone Workshop VPK. Switching reloads materials and may briefly pause rendering. Publication and optional companion distribution remain pending review/approval. The images here are diagnostic lab shots, not approved listing media.
