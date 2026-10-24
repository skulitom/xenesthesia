# Xenesthesia release review

Owner explicitly authorized Workshop publication on 24 October 2026, requiring
latest in-game screenshots and no generated cover. This supersedes the previous
hold on uploads. The approved runtime is SHA-256
`0bb326b0b729c0b348af976e983ba5cc125c0a092fbf4e2df265d2795385beef`.

The package contains 2,662 runtime files, including 2,632 generated material
definitions, twenty compiled vertex shaders and three original procedural VTFs.
The latest material coverage change passed 42 checks. Native validation includes
the reported canal stairwell, architectural cutouts and a City 17 storefront;
see CURRENT-VALIDATION.md and COVERAGE.md. The asset audit covers 68 playable
original-campaign maps; it is not a complete campaign playthrough.

The owner's iterative playtests approved the restrained motion and colour flow.
Combine pulses retain the twice-reduced strength. Existing full-quality timing
records distinguish warm runs from first-observed stalls; no universal frame-rate
or stutter-free claim is made. Character/cinematic and platform limits are stated
on the listing. No visual-quality reduction was made for release.

The Workshop runtime is content only. The local preview F5 companion is not
shipped and is not advertised as a Workshop feature. Disable/restart is the
supported Workshop removal path only after also removing the required early-load
launch option. No user key bindings change automatically. Clean-install testing
exposed a late-mount shader cache crash; loading the subscribed VPK through
`-insert_search_path` before shader initialization preserves the full visuals.
The title and beginning of the listing explicitly flag the required setup.

The thumbnail and gallery come from the current runtime. gameplay-media.json
records their source paths and hashes. Generated artwork and its prompt are
excluded from staging. The staging tool verifies every runtime file and the
manual-install ZIP before any upload.

Published publicly on 24 October 2026 as item 3826155980. Steam accepted the content,
gallery and public-visibility updates. The logged-out page shows the correct real
gameplay cover, three gallery images, setup instructions and Subscribe control.
Publication receipts and subscribed-only checks are in PUBLICATION.md.
