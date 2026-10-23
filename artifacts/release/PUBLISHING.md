# Publication handoff — local only

The owner has explicitly prohibited creating or uploading a Workshop item until
they give a go-ahead. Do not treat approving the visual balance, launching the
preview or producing this folder as publication approval.

## Prepared fields

- Game: Half-Life 2, Steam app 220.
- Proposed title: Xenesthesia — Breathing Textures & Prismatic Colour.
- Description: `workshop-description.txt`.
- Runtime folder: `workshop-content` in the staged release candidate.
- Preview: `media/cover-workshop.png` (512×512); JPEG alternative also included.
- Genuine gallery: `media/coast.jpg`, `media/ravenholm.jpg`.
- Local manual-install package: `xenesthesia-manual-install.zip`.

Keep review documents, prompts, private settings and the manual-install ZIP out
of the Workshop runtime folder. Check manifest hashes again if any file changes.
Regenerate captures if the shader's visual appearance changes after this review.

## After explicit approval

Use the game's native Workshop uploader under Extras > Workshop > My Uploads.
Select the prepared runtime folder and separate preview image. Confirm the native
uploader accepts the folder and image before submitting. Initially use private
visibility for the owner to validate the uploaded installation; publication
visibility follows the scope of their approval. Preserve the created item ID.

Close HL2 and temporarily remove the local development VPK before testing the
subscription. Verify the actual Workshop download matches the intended runtime,
then load a normal HL2 save from the main menu. Recheck colour, material motion,
hands/weapons, HUD, toggle and addon disable/restart. A locally installed VPK can
otherwise mask a broken Workshop installation. Record results in VALIDATION.md.

If Steam requests its contributor agreement, the owner must complete that step.
Do not claim successful publication from a created ID or an upload button click;
confirm the result, visibility, page contents and real subscribed installation.

## Format references

Valve's [Workshop implementation guide](https://partner.steamgames.com/doc/features/workshop/implementation)
describes separate item creation and upload operations, the content directory,
preview image and completion callbacks. Its [ISteamUGC reference](https://partner.steamgames.com/doc/api/ISteamUGC#AddItemPreviewFile)
specifies an under-1-MB limit for additional image previews. The staged thumbnail
exports and original game screenshots are all conservatively below 1,000,000 bytes.
The full-resolution cover master is retained for review, not used as the thumbnail.
