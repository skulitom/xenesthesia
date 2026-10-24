# Xenesthesia publication record — 24 October 2026

Public item: https://steamcommunity.com/sharedfiles/filedetails/?id=3826155980

Title: **Xenesthesia - Breathing Textures & Prismatic Colour [Setup Required]**

The owner explicitly authorized publication with current in-game screenshots and
without the generated cover. Steam accepted the native upload, gallery update and
public visibility update. Logged-out browser verification shows the actual listing,
Subscribe control, required setup instructions and all four gameplay images.
`workshop-public.png` and `workshop-public.txt` record that public-page check.

## Content and receipts

- Original Half-Life 2, app 220; published file ID **3826155980**.
- Native uploader completed at approximately 13:57 UTC, 24 October 2026.
- Downloaded content manifest: **1056018477674889439**.
- Gallery submission: 14:12:27 UTC; callback result **1 (OK)**, received true,
  failed false, agreement not required.
- Public visibility submission: 14:14:04 UTC; callback result **1 (OK)**,
  received true, failed false, agreement not required.
- Unauthenticated GetPublishedFileDetails returned result 1, visibility **0**,
  banned **0**, correct title and exact published description.
- Local receipts: `artifacts/workshop-gallery.json`, `workshop-publish.json`,
  `workshop-web-details.json` and `workshop-item.json` (operational records).

Approved runtime SHA-256:
`0bb326b0b729c0b348af976e983ba5cc125c0a092fbf4e2df265d2795385beef`.
All **2,662** files in the real subscribed split VPK matched the build manifest
byte for byte, including 2,632 materials, twenty shaders and three original VTFs.

Downloaded archives:

| Archive | Bytes | SHA-256 |
| --- | ---: | --- |
| workshop_000.vpk | 18313920 | b10e142d0ad8444ffb667e74616fc53fa7be894bcf37e05466188b7e0c4586c3 |
| workshop_dir.vpk | 96750 | 86d29cc7f90732b70a0547daa2047ffe95023ab61410274ee633c71df1213ab4 |

## Required setup and clean-install validation

Ordinary late Workshop mounting failed clean-install testing with a shader
decompression error. This is a real retail Source loading limitation, not a
corrupt download. Subscription alone is **not** a supported installation method.
The public title and beginning of the description flag the required setup:

```
-insert_search_path "../../workshop/content/220/3826155980/workshop_dir.vpk"
```

Adding that option loads the actual subscribed archive before shader cache
initialization. The complete approved runtime remains unchanged. No reduction
in animation quality was made for publication.

The local development VPK was moved out of the game, active loose material/shader
overrides were absent, and the F5 companion was not running. Using only the actual
download plus this startup option, native Anode checks passed:

- Main menu > New Game > A Red Letter Day, loading d1_trainstation_05.
- Two stationary lab captures show independently evolving colour and tank flow.
- Transition to d1_canals_01: reported wall and grates, crowbar and readable HUD.
- Return to d1_trainstation_05 without a shader crash.
- Remove the startup option, disable the item, restart: stock lab rendering and
  no addon mounting. The checkbox alone cannot disable an explicit startup path.

Proof captures are in `verification/`. The existing 42 automated checks passed
before publication; no runtime change followed. This was not a full campaign,
platform or cinematic regression; the listing retains those limits and the
possibility of first-use loading stutters.

The local game is closed and the subscribed item is disabled after rollback
testing. No persistent Steam launch options were changed. The backed-up development
VPK is retained outside the game in the private artifacts directory. City 17 ASCII
remains disabled. Ordinary game launches therefore retain stock rendering.

## Published media

- Main thumbnail: `gameplay/lab.jpg`, a new native screenshot of this runtime.
- Gallery: `gameplay/carpet.jpg`, `gameplay/canals.jpg`, `gameplay/storefront.jpg`.
- Provenance and exact hashes: `gameplay-media.json`.
- Four genuine gameplay images total; no generated artwork or generated cover.

The public browser check confirmed the lab thumbnail on the right and the three
gallery previews. Still images are explicitly described as showing only a moment
of the animated effects.
