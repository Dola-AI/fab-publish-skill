# Common listing checks (every Fab product)

Applies to every listing, whatever the engine or format. Paraphrased from Fab's public docs (snapshot 2026-11-18); follow the source link for the binding wording.

Columns: **Verify** is `auto: <id>` when it can be decided from the files alone (the optional `fab_audit.py` uses the same ids), `manual` when you read files or ask the user, `portal` when it can only be checked in the Fab publisher portal after upload. **Severity**: blocker (Fab will decline or the upload fails), review risk (a common reason for "Changes needed"), recommended (better listing, not enforced).

## Account and publisher profile

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| C.acct.1 | The user has a Fab publisher account: signed in at fab.com, clicked Publish, accepted the Distribution Agreement, chose a Creator Code. | ask | blocker | [Get started][GS] |
| C.acct.2 | Trader verification, tax form (W-9 or W-8BEN) and payout details are done, or the user knows they are needed before money can be paid out. | ask | blocker for paid | [TR 1.3.b][TR], [DA s.5d-e][DA] |
| C.acct.3 | Publisher name is not offensive and does not use Epic, Unreal or other companies' names. | ask | review risk | [TR 1.3.a][TR] |
| C.acct.4 | A support channel is set in the publisher profile (Publish Settings) and someone watches it. | ask | blocker | [TR 1.1.b][TR] |

## Listing text

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| C.text.1 | Title says what the product is, short (Fab suggests about 30 characters), no personal data. | manual | recommended | [Publishing: Title][PUB] |
| C.text.2 | All listing text is English with correct spelling and grammar. | manual | review risk | [TR 1.8.1.a][TR] |
| C.text.3 | Description covers what it is, how to use it, what is included (asset counts, specs) and prerequisites. | manual | review risk | [Publishing: Description][PUB] |
| C.text.4 | Anything shown in media but not included (a road under a car, demo characters) is stated as not included. | manual | review risk | [Publishing: Create or edit][PUB], [TR 1.8.6.a][TR] |
| C.text.5 | Technical information fields are all filled, and dependencies, prerequisites and requirements are named. | manual | blocker | [TR 1.8.4.a-b][TR] |
| C.text.6 | Experimental or beta engine features the product relies on are named in the description. | manual | blocker | [TR 4.3.1.d][TR] |
| C.text.7 | No savings claims ("-50%", "sale") in title, thumbnail or description; Fab shows real discounts itself. | manual | blocker | [Bundles: pricing][BUN] |
| C.text.8 | No IDs, credentials or private data in title or description. | manual | review risk | [Publishing: Description][PUB] |

## Category, format and tags

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| C.cat.1 | Category (product type) is the most relevant one. Fab's product types: 2D Assets, 3D Models, Animations, Audio, Education & Tutorials, Environments, Game Systems, Game Templates, HDRI, Material & Textures, MetaHuman, Smart Assets, Tools & Plugins, User Interfaces (UI), Visual Effects (VFX). | ask | review risk | [TR 1.8.2.a][TR], [Formats table][AFF] |
| C.cat.2 | Each uploaded format holds only that format (FBX upload = FBX files only); formats suit the product type. | auto: dcc.one_format; manual | blocker | [TR 1.8.3.a, 2.1][TR] |
| C.cat.3 | Tags are accurate; use Fab's filter tags where they fit (style, theme, technical features, engine features, materials). Use all tag slots. | manual | review risk | [TR 1.8.5.a][TR], [Publishing: Tags][PUB], [Brand Hub][BH] |
| C.cat.4 | No executables, installers or archives other than .zip anywhere in the upload; zip64 archives are not supported. | auto: files.forbidden, zip.zip64 | blocker | [TR 2.2][TR], [Unsupported types][UNS] |
| C.cat.5 | Upload zip is not encrypted or password-protected. | auto: zip.encrypted | blocker | [Unreal format][AFF] |
| C.cat.6 | Size limits: Unreal about 15 GB (larger is reviewed case by case), Unity follows the Asset Store limit (6 GB), Additional Files 6 GB each and up to 3, other formats one file per type. | auto: package.size | review risk | [File Format Requirements][AFF] |

## Media

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| C.media.1 | A thumbnail exists and clearly shows the product (Fab also derives search tags from it). | ask | blocker | [Get started: Creating a Listing][GS], [Publishing: Thumbnail][PUB] |
| C.media.2 | At least one gallery item: image, video or 3D preview. | ask | blocker | [Get started][GS] |
| C.media.3 | Gallery images at least 1920x1080, under 3 MB each, JPEG or PNG, under 25 MB in total. | manual (if files given) | blocker | [Media Gallery Images][AFF] |
| C.media.4 | Videos 1920x1080, up to 300 MB, MP4/MOV/WEBM. 3D previews under 500 MB. | manual | blocker | [Media Gallery Videos][AFF] |
| C.media.5 | Media shows what the product really contains. Packs: include an overview image of all assets on a plain background. | manual | review risk | [TR 1.8.6.a][TR], [Publishing: Images][PUB] |
| C.media.6 | No standalone Unreal Engine or MetaHuman logos on thumbnails. Use the official "Made for" or "Powered by" marker, or no marker. | manual | review risk | [Brand Hub: thumbnails][BH], [TR 1.8.6.b][TR] |
| C.media.7 | Type-specific media: animations need a 3D model or video showing them; audio needs a preview URL; Blueprint/Smart Asset projects need a demo download or video; Niagara VFX need a video. | ask | blocker | [TR 4.1.1, 6.1.1][TR], [Content guidelines][AFF] |

## Licence, price and AI

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| C.lic.1 | Licence chosen: Standard (free or paid) or CC-BY (free only). | ask | blocker | [Licenses][LIC] |
| C.lic.2 | Standard listings set a price for both the Personal and the Professional tier (may be equal). | ask | blocker | [Licenses][LIC] |
| C.lic.3 | Price in USD from Fab's preset ladder: $1 steps to $100, then $5, $10, $25, $100 steps; all end in .99 except $0; over $1,500 needs Fab Support. Price should match the value. | ask | blocker | [Pricing][LIC], [TR 1.8.7.a][TR] |
| C.lic.4 | Files do not ship a custom licence that tries to replace the Fab EULA (a third-party notice file is fine). | manual | review risk | [DA s.3f.v][DA] |
| C.ai.1 | "Created with AI" is set if a material part (characters, backgrounds, meshes, textures, code, audio) came from generative AI. Not needed for tools that only edit your work (content-aware fill, upscaling). Mislabelling can get the product removed. | ask | blocker | [TR 1.8.8.a][TR], [DA s.18(k)(ii)][DA], [AI declaration][NOAI], [AI update][AIU] |
| C.ai.2 | Optional "Disallow use by generative AI" (NoAI) only works with the Standard licence, not CC-BY. | ask | recommended | [Licenses: NoAI][LIC], [DA s.18(k)(i)][DA] |
| C.mat.1 | Maturity rating covers every image, file and linked page; alcohol, tobacco and prescription drugs count. | ask | blocker | [TR 1.8.9.a][TR], [Mature][MAT] |
| C.promo.1 | Paid placement or promotion of a real brand is declared as Promotional Content. | ask | blocker | [TR 1.8.10.a][TR] |

## Rights and third-party content

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| C.ip.1 | The user owns or has licensed everything; no unlicensed brands, logos, trademarks or Epic IP (game names, characters). | ask | blocker | [Brand names][BRAND], [DA s.3a, 3g][DA], [Content guidelines][ECG] |
| C.ip.2 | No Quixel Megascans content inside the product (it cannot be redistributed). | ask | blocker | [Megascans][MEGA] |
| C.ip.3 | MetaHuman characters made in the web MetaHuman Creator (UE 5.5 or earlier) are not sold; ones made in UE 5.6+ may be. | ask | blocker | [MetaHuman][MHC] |
| C.ip.4 | Epic sample content is only for demo, kept in a separate folder, not the majority, not Quixel/MetaHuman/free-collection assets, and listed separately in the technical information. | manual | blocker | [Demo content][DEMO], [TR 4.3.1.g][TR] |
| C.ip.5 | Unmodified public-domain content is only supporting material, and its source is cited with a link in the technical information. | ask | blocker | [DA s.3f.iv][DA] |
| C.ip.6 | Third-party software (fonts, sounds, code, libraries, APIs) is declared on the listing; code plugins also fill Epic's third-party form. | auto: legal.thirdparty_*; ask | blocker | [TR 4.2.5][TR] |
| C.ip.7 | No GPL, AGPL, LGPL (except dynamic linking), EPL, MS-PL or CC-BY-SA material. | auto: legal.copyleft | blocker | [DA s.3c, 3f.vi][DA] |
| C.ip.8 | Content is allowed under Epic's content guidelines (no hate, no pornography, no real-world gore, no scams or malware). | manual | blocker | [Content guidelines][ECG], [DA s.3g][DA] |

## Documentation and support

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| C.doc.1 | Products that need setup knowledge come with free English docs (web page, txt/pdf, comments, video or in-editor tutorial). | auto: docs.present; ask | blocker | [TR 4.3.8][TR] |
| C.doc.2 | Download links (docs, demos, example projects) open a page, do not start a download automatically, and need no permission request. | manual (try the link) | blocker | [TR 4.3.8.d][TR], [Declined][DECL] |
| C.doc.3 | Additional Files relate to this listing and are included in the maturity rating. | ask | review risk | [TR 3.1.a][TR] |

## Review and after publishing (tell the user; nothing to fix in files)

- Review looks at accuracy versus the listing, technical and functional quality, and whether it adds value and is not trivially reproducible. [How content is reviewed][REV]
- Most common declines: too little content, not enough quality, wrong file format, broken or permission-gated download link, unlicensed IP. Do not resubmit without making the requested changes. [Declined][DECL]
- Status flow: Draft, Pending approval, Changes needed or Approved or Declined, Pending Publication, Live. A Declined listing needs a new listing. [Listing statuses][PUB]
- On submit, choose Automatic activation (goes live after approval) or Manual activation (you click Publish). [Send for review][PUB]
- The docs give no turnaround for a first review. Updates to a live listing are "most" processed within 24 hours. [Updating a listing][UPD]
- Changes to type, category, licence, prices, tags, AI selections, promo declaration, 3D detail fields and platforms go live without review; title, description, thumbnail, media, open-text technical details and files are reviewed. [Review requirements for updates][PUB]
- Code plugins are built by Fab for each selected engine version; a failed build sends the listing back to Draft with the log. [Automated builds][PUB]
- A product can only join a sale 30 days after first publishing; seller share is 88%; payouts monthly from $100. [TR 1.7.1.c, 1.5][TR], [Get started: Payout][GS]
- Publishers keep supporting and updating products (bug fixes, compatibility) while they are listed. [DA s.4a][DA], [TR 1.1.a][TR]

[TR]: https://www.fab.com/o/technical-requirements
[AFF]: https://dev.epicgames.com/documentation/fab/asset-file-format-and-structure-requirements-in-fab
[PUB]: https://dev.epicgames.com/documentation/fab/publishing-assets-for-sale-or-free-download-in-fab
[GS]: https://dev.epicgames.com/documentation/fab/publisher-get-started-in-fab
[LIC]: https://dev.epicgames.com/documentation/fab/licenses-and-pricing-in-fab
[BUN]: https://dev.epicgames.com/documentation/fab/bundles
[DA]: https://www.fab.com/distribution-agreement
[BH]: https://brand.epicgames.com/document/411#/-/product-thumbnails-images-1
[UNS]: https://support.fab.com/s/article/Unsupported-File-Types-on-Fab?language=en_US
[NOAI]: https://support.fab.com/s/article/Introducing-NoAI-meta-tags-and-Created-with-AI-self-declaration?language=en_US
[AIU]: https://forums.unrealengine.com/t/update-on-products-generated-with-ai/2523501
[MAT]: https://support.fab.com/s/article/Fab-Why-was-my-product-marked-Mature?language=en_US
[BRAND]: https://support.fab.com/s/article/Can-I-publish-products-that-include-brand-names-or-logos?language=en_US
[MEGA]: https://support.fab.com/s/article/Can-I-use-Quixel-Megascans-content-in-my-Fab-product?language=en_US
[MHC]: https://support.fab.com/s/article/Can-I-sell-characters-created-with-MetaHuman-Creator-on-Fab?language=en_US
[DEMO]: https://support.fab.com/s/article/Fab-Demo-Content-Usage?language=en_US
[ECG]: https://legal.epicgames.com/en-US/epicgames/content-guidelines
[DECL]: https://support.fab.com/s/article/Why-was-the-submission-declined?language=en_US
[REV]: https://support.fab.com/s/article/How-is-content-reviewed?language=en_US
[UPD]: https://support.fab.com/s/article/Updating-your-Product-Listing-Page?language=en_US
