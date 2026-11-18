# Question bank

Ask only what the files and the audit facts cannot answer. Before each round, fill in everything you already know and show it as a "detected" line the user can correct, instead of asking. Ask one round at a time, at most about five questions, and accept short answers ("free", "5.5-5.7, Win+Mac", "no AI").

Each question lists: why it matters, where the answer is written back (see `fixes.md` W-* recipes and `fab-listing-template.md`), and when to skip it.

## Round 0: intake (always first, often answered by detection)

| # | Question | Why | Written to | Skip when |
|---|---|---|---|---|
| 0.1 | Which engine or format is this for: Unreal Engine, UEFN, Unity, MetaHuman (.mhpkg), or plain 3D/DCC files (FBX, OBJ, GLB, GLTF, USD/USDZ, Blender, Maya, 3ds Max, Cinema 4D)? | Decides which rules and which upload slot apply. Fab sells all of these. | FAB_LISTING.md "Formats" | the audit detected exactly one type (show it and ask to confirm only if there were several) |
| 0.2 | Which Fab product type? 2D Assets, 3D Models, Animations, Audio, Education & Tutorials, Environments, Game Systems, Game Templates, HDRI, Material & Textures, MetaHuman, Smart Assets, Tools & Plugins, User Interfaces (UI), Visual Effects (VFX). Or a bundle of existing listings? | Sets minimum content, required maps and media, and the category buyers browse. | FAB_LISTING.md "Category"; .uplugin `Category` | it is obvious (a C++ editor plugin is Tools & Plugins; offer your guess with a one-line reason) |
| 0.3 | Unreal content only: should buyers merge it into their project (Asset Pack) or start from it (Complete Project)? | Asset Packs may not rely on Level Blueprints or required .ini settings. | FAB_LISTING.md "Distribution method" | code plugins, Unity, UEFN |
| 0.4 | Do you already have a Fab publisher account with payout and tax set up? | No account means the publish steps start with sign-up and trader verification. | publish steps only | user said so earlier |

## Round 1: listing basics

| # | Question | Why | Written to | Skip when |
|---|---|---|---|---|
| 1.1 | Product title? (Fab suggests about 30 characters.) | Search and first impression. | FAB_LISTING.md; .uplugin `FriendlyName`; package.json `displayName` | descriptor already has a good name: propose it |
| 1.2 | In one or two sentences, what does it do and who is it for? | Becomes the short and long description. | FAB_LISTING.md; .uplugin `Description`; package.json `description`; README | descriptor/README already says it: propose a draft instead |
| 1.3 | Tags: any must-have words? I will propose the rest from Fab's filter tags. | Tags drive filters and search. | FAB_LISTING.md | never ask for a full list; draft it |
| 1.4 | Version number for this release? | Changelog and descriptor version. | .uplugin `VersionName`/`Version`; package.json `version`; CHANGELOG | already set and sensible |

## Round 2: compatibility

| # | Question | Why | Written to | Skip when |
|---|---|---|---|---|
| 2.1 | Which engine versions have you tested it in? (Unreal: the latest must be included on first submission; code plugins need one upload per version.) | A Fab requirement, and code plugins are built per version. | .uplugin `EngineVersion` (one per zip); .uproject `EngineAssociation`; package.json `unity`/`unityRelease`; FAB_LISTING.md | descriptor already pins one and the user only targets that |
| 2.2 | Which target platforms (Windows, Mac, Linux, iOS, Android, consoles)? | Listing field and .uplugin platform allow lists must agree. | .uplugin `PlatformAllowList` per module; FAB_LISTING.md | allow lists exist and user confirms them |
| 2.3 | Unity: which render pipelines (Built-in, URP, HDRP)? | Unity 6.5+ submissions must support URP or HDRP; buyers filter by it. | FAB_LISTING.md; README | not Unity |
| 2.4 | Does it need anything else installed: engine plugins, other Fab products, SDKs, accounts or keys? Any experimental or beta engine features? | Dependencies must be named; experimental features must be stated. | FAB_LISTING.md technical details; README | audit found none and the user confirms |

## Round 3: price and licence

| # | Question | Why | Written to | Skip when |
|---|---|---|---|---|
| 3.1 | Free or paid? If paid, Personal-tier and Professional-tier prices in USD (ending .99; they can be equal)? | Both tiers are required for Standard; prices come from a fixed ladder. | FAB_LISTING.md | never skip |
| 3.2 | Licence: Standard (free or paid) or Creative Commons Attribution (free only)? | CC-BY cannot be used with NoAI or in bundles. | FAB_LISTING.md; LICENSE note in README | paid (must be Standard) |
| 3.3 | Do you want to forbid use of the product for training generative AI (NoAI)? | Optional; only with Standard. | FAB_LISTING.md | CC-BY |

## Round 4: disclosures (legal; explain briefly why you ask)

| # | Question | Why | Written to | Skip when |
|---|---|---|---|---|
| 4.1 | Was generative AI used to make any meaningful part (meshes, textures, images, audio, code, text)? Upscaling or content-aware fill alone does not count. | "Created with AI" is mandatory when it applies; wrong answers can get the product removed. | FAB_LISTING.md | never skip |
| 4.2 | Does it include anything you did not make: fonts, sounds, textures, code libraries, scans, Epic sample content, Megascans, public-domain material? What licences? | Third-party content must be declared and licensed; Megascans and some licences are not allowed. | Third-Party Notices file; FAB_LISTING.md; Epic third-party form for code plugins | audit found nothing and user confirms "all mine" |
| 4.3 | Any real brands, logos, game characters or trademarks in the content or media, and do you have rights to them? Any paid promotion? | Unlicensed IP is a top decline reason; promotions must be declared. | FAB_LISTING.md | user already answered "all original" |
| 4.4 | Any mature content: violence, gore, nudity, alcohol, tobacco, drugs, gambling? | The maturity rating must cover files, media and linked pages. | FAB_LISTING.md | obvious from type (an editor tool) |

## Round 5: support and docs

| # | Question | Why | Written to | Skip when |
|---|---|---|---|---|
| 5.1 | Documentation URL, or should I write a README/docs page in the package? | Docs are required when setup is needed; links must not auto-download. | .uplugin `DocsURL`; package.json `documentationUrl`; README; FAB_LISTING.md | DocsURL set and reachable |
| 5.2 | Support contact (email, Discord, forum, website)? Who should be named as creator? | Support channels are mandatory and must be monitored. | .uplugin `SupportURL`, `CreatedBy`, `CreatedByURL`; package.json `author`; README; copyright headers | already in descriptor |
| 5.3 | Code plugins: is there an example project, and where will it be downloadable? | Strongly encouraged; goes in technical information as a link. | FAB_LISTING.md technical details | not a code plugin |

## Round 6: media

| # | Question | Why | Written to | Skip when |
|---|---|---|---|---|
| 6.1 | Do you have a thumbnail and gallery images (1920x1080 or larger, under 3 MB, JPEG/PNG)? A video? If they are in the folder, tell me where. | A thumbnail plus one gallery item are required; type-specific media (animation video, audio preview, VFX video, Blueprint demo) are required too. | FAB_LISTING.md media checklist | user pointed at the files (check sizes yourself) |
| 6.2 | Audio: preview link? Animations/VFX: video link? Blueprints: demo or video link? | Required by type. | FAB_LISTING.md long description | type does not need it |

## Things you can only check after upload or in the portal (say so plainly)

FabURL product ID (exists only after the listing is created), Fab's automatic build of code plugins, auto-filled 3D technical fields, the 3D viewer thumbnail, the forum-thread option, the third-party software form, the review result itself.
