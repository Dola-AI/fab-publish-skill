# Audio, VFX, animations, HDRI, 2D, UI, MetaHuman and other product types

The remaining Fab product types. Also read `common-listing.md` and the engine reference. Minimum-content numbers below come from Fab's Unreal content guidelines; Unity products follow `unity.md`. Paraphrased from Fab's docs (snapshot 2026-11-18).

## Audio

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| A.aud.1 | Minimum: music 5 tracks; sound effects about 20 good sounds; ambient 10 tracks. | auto: facts.audio_file_count; ask | blocker | [AFF: Audio][AFF] |
| A.aud.2 | The long description links an audio preview (for example a SoundCloud or YouTube page). | ask | blocker | [TR 4.1.1.b, 6.1.1.b][TR], [AFF: Audio][AFF] |
| A.aud.3 | Unreal audio is imported from .wav; files are as high quality as possible with no unwanted hitching or distortion. | auto: audio.wav_import, facts.audio_formats; manual (listen) | blocker | [TR 4.3.4.a-b][TR] |
| A.aud.4 | MetaSounds: tidy graphs, no loose nodes, no errors or warnings, inputs commented, author/display name/description set, presets clearly organised; UE 5.0+ only. | manual (editor) | blocker | [TR 4.3.4.c-e][TR], [AFF: MetaSounds][AFF] |
| A.aud.5 | MetaSounds listings carry the exact line "This product supports MetaSounds for Unreal Engine 5.0+" on the product page; Asset Packs include docs (or a link to Epic's MetaSounds docs) on enabling MetaSounds. | ask | blocker | [TR 4.3.4.f-g][TR] |
| A.aud.6 | MetaSounds products contain MetaSound Source and/or Patch assets and offer real value beyond tutorials. | manual | blocker | [AFF: MetaSounds][AFF] |
| A.aud.7 | Technical details list sample rate, bit depth, channel count and durations. The audit prints these for .wav files. | auto: facts.audio_formats | recommended | [Unity 3.1.b][UAS], [TR 1.8.4][TR] |

## Visual effects

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| A.vfx.1 | Niagara VFX: at least 1 unique effect, an overview map, and a video in the listing showing the effects. | manual, ask | blocker | [AFF: Niagara VFX][AFF] |
| A.vfx.2 | Emitters have meaningful names; "Particle Emitter" only when it is the sole emitter. | manual (editor) | review risk | [TR 4.3.3.6.b][TR] |
| A.vfx.3 | Effects seen at several distances have LODs; effects are optimised and scaled for their use. | manual | review risk | [TR 4.3.3.6.a, c][TR] |

## Animations

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| A.anim.1 | At least 10 unique animations, plus an overview map. | manual | blocker | [AFF: Animation][AFF] |
| A.anim.2 | Listing shows the animations: a 3D model in the gallery or a video URL in the long description. | ask | blocker | [TR 4.1.1.a][TR] |
| A.anim.3 | Clean, consistent, and do what they claim. | manual | blocker | [TR 4.3.3.3.a][TR] |
| A.anim.4 | Meant for MetaHumans? Also follow the MetaHuman rules below. | ask | blocker | [AFF: Animation][AFF] |

## HDRI

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| A.hdri.1 | At least 5 unique skyboxes, plus an overview map in Unreal. | auto: detection (hdri-files); manual | blocker | [AFF: HDRI][AFF] |

## 2D assets and UI

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| A.2d.1 | Minimum: 2D art 25, backgrounds 10, decals 10, icons 25, landscape brushes 25, sprite animations 5 to 10+. | manual | blocker | [AFF: 2D Assets][AFF] |
| A.2d.2 | Overview map only if the product has working UI elements or game-ready animated sprites. | manual | blocker | [AFF: 2D Assets][AFF] |
| A.ui.1 | UI: at least 25 assets and 1 complete UI Blueprint system. | manual | blocker | [AFF: UI][AFF] |

## Education, Game Systems, Game Templates, Tools

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| A.edu.1 | Minimum judged per product; thorough documentation is required (video, written, Blueprint comments, in-level text or in-editor tutorial). | auto: docs.present; ask | blocker | [AFF: Education, Game Systems][AFF] |
| A.edu.2 | Game Systems and Templates need a demo map unless they only hold well-documented functions. See `unreal-blueprint-and-project.md`. | manual | blocker | [AFF: Game Systems][AFF] |

## MetaHuman (.mhpkg)

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| A.mh.1 | Characters, clothing and grooms are a single .mhpkg in a zip, not nested zips, made in UE 5.6 or later. | auto: metahuman.single | blocker | [TR 5.2.1][TR], [AFF: MetaHuman][AFF] |
| A.mh.2 | .mhpkg no larger than 1.5 GB; clothing has materials applied. | auto: metahuman.size; manual | review risk | [AFF: MetaHuman][AFF] |
| A.mh.3 | Technical information states MetaHuman skeleton support and every supported body type combination, in the format Fab's guide shows. | ask | blocker | [AFF: MetaHuman][AFF], [TR 5.3.2.2.a][TR] |
| A.mh.4 | For review, a download link to a project with imported MetaHumans (one per supported body type). | ask | blocker | [AFF: MetaHuman][AFF] |
| A.mh.5 | "MetaHuman" in the name only to say it works with MetaHuman, never implying Epic made it. | manual | review risk | [AFF: MetaHuman][AFF] |
| A.mh.6 | Same file-structure, naming, 140-character path, redirector, docs, texture and skeleton rules as Unreal content. | manual | blocker | [TR 5.3][TR] |
| A.mh.7 | Creator-made MetaHumans from the web tool (UE 5.5 or earlier) cannot be sold. | ask | blocker | [MetaHuman Creator][MHC] |

## Additional Files and Paid Random Items

- Additional Files: up to 3 per listing, 6 GB each; they must relate to the listing and count towards maturity. [AFF][AFF], [TR 3.1.a][TR]
- "Paid Random Item" is only defined in the docs (items bought to obtain a random reward). Nothing in the docs explains how to list one; treat products that sell randomised rewards as a question for Fab Support before publishing. [Paid random item][PRI]

[TR]: https://www.fab.com/o/technical-requirements
[AFF]: https://dev.epicgames.com/documentation/fab/asset-file-format-and-structure-requirements-in-fab
[UAS]: https://assetstore.unity.com/publishing/submission-guidelines
[MHC]: https://support.fab.com/s/article/Can-I-sell-characters-created-with-MetaHuman-Creator-on-Fab?language=en_US
[PRI]: https://dev.epicgames.com/documentation/fab/paid-random-item
