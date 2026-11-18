# UEFN Source and bundles

Paraphrased from Fab's docs (snapshot 2026-11-18). Also read `common-listing.md`.

## UEFN Source (.uefnproject)

UEFN has no export or package command and cannot publish to Fab from inside the editor: you zip the project folder yourself. Fab does not open the project or check that references resolve, so a zip that uploads fine can still be broken for buyers. Testing is on you. [UEFN guide][UEFN]

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| F.dir.1 | One UEFN project per zip: the project file, its plugin file and all content. Not encrypted. | auto: package.single, zip.encrypted | blocker | [TR 6.2.1.a][TR], [UEFN: Step 3][UEFN] |
| F.dir.2 | No Python files (.py) anywhere. | auto: python.forbidden | blocker | [AFF: UEFN Script Files][AFF] |
| F.dir.3 | `Saved` and `Intermediate` removed; no unused folders. | auto: structure.local_folders | blocker | [UEFN: Step 2-3][UEFN] |
| F.dir.4 | Names: English letters, digits, underscores; not vague; paths 140 characters or less including the top folder. | auto: naming.charset, naming.vague, paths.length | blocker | [TR 6.3.6][TR] |
| F.dir.5 | Assets sorted into folders by type or set. | manual | review risk | [TR 6.3.6.2.b][TR] |
| F.code.1 | Verse compiles; project passes UEFN validation with no errors or meaningful warnings; Verse components and NPC behaviours clean. | manual (UEFN) | blocker | [TR 6.3.1.d][TR], [UEFN: Step 1][UEFN] |
| F.code.2 | Redirectors fixed (Content Browser: Update Redirector References). | auto: content.redirectors; manual | blocker | [TR 6.3.1.f][TR] |
| F.code.3 | Cooks and stays within Fortnite memory limits. | manual (UEFN) | blocker | [UEFN: Step 1][UEFN] |
| F.code.4 | Scene Graph practice: standard traversal, no repeated wide scans during play, narrow Scene Events, clear parent/child roles. | manual | review risk | [AFF: Entities and Prefabs][AFF] |
| F.map.1 | A level demonstrating anything visual; no z-fighting or overlapping polygons. | manual | blocker | [TR 6.3.2][TR] |
| F.art.1 | Textures at most 8192 px (4096 or less recommended), power of two where it applies. | auto: textures.* (loose images) | blocker | [TR 6.3.3.1][TR] |
| F.art.2 | Meshes: no seams or material defects, collision, LODs stated in the technical details (Includes LODs: Yes/No and count). | ask, manual | blocker | [TR 6.3.3.2][TR], [UEFN: Step 5][UEFN] |
| F.art.3 | Characters rigged and scaled to the MetaHuman skeleton (or custom skeleton with animations); skeleton changes documented in Additional information. | manual | blocker | [TR 6.3.3.4][TR] |
| F.art.4 | Audio imported from .wav, clean. | manual | blocker | [TR 6.3.4][TR] |
| F.list.1 | Description declares whether third-party software of any kind is included or used. | ask | blocker | [TR 6.2.2.a][TR], [UEFN: Step 5][UEFN] |
| F.list.2 | Animated products show a 3D model or video; audio products link a preview; Smart Asset projects link a demo or video. | ask | blocker | [TR 6.1.1][TR] |
| F.list.3 | Promoted as usable in Fortnite? It must follow the current Fortnite Developer Rules. | ask | blocker | [DA s.3i][DA] |
| F.test.1 | Before upload: import the zip into a clean UEFN project; it opens, references resolve and the demo level works. | ask (user runs it) | blocker | [UEFN: Step 4][UEFN] |

Licensing note: UEFN Source is sold under the Standard licence only; there is no Reference Only tier for source. Buyers who already downloaded keep their version when you update; describe changes in the Changelog. [Licenses][LIC], [Publishing: UEFN updates][PUB]

## Bundles

A bundle groups 2 to 50 of your own live listings under one price and page. It is built in the portal (Publish > Listings > Create Product > Bundle), not from files, so the audit script has nothing to scan; check the listings instead. [Bundles][BUN], [Build a bundle][BB]

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| B.1 | 2 to 50 listings, all yours, all live, none with a draft or pending version in progress. | ask | blocker | [Bundles: What you can put][BUN] |
| B.2 | No bundle inside a bundle; each listing is in at most 3 live bundles. | ask | blocker | [Bundles][BUN] |
| B.3 | Same licence configuration across all listings: each has Personal + Professional (optionally plus UEFN Reference only), or each has Professional + UEFN Reference only. No CC-BY listings. | ask | blocker | [Bundles: Licence compatibility][BUN] |
| B.4 | Required bundle fields: title, description, a price per licence tier, tags, thumbnail, media gallery unique to the bundle. | ask | blocker | [Build a bundle: details][BB] |
| B.5 | No savings claims in the title, thumbnail or description; Fab shows the price comparison itself. | manual | blocker | [Bundles: pricing][BUN] |
| B.6 | Maturity, Created with AI, Allows AI and Promotional content are inherited from the listings and cannot be lowered. | inform | n/a | [Bundles: Bundle information][BUN] |
| B.7 | Know what unlists a live bundle: changing a listing's licence mix, adding UEFN Reference, Mature to Not Mature, either AI flag, or a listing being taken down. Contents cannot be changed after publishing. | inform | n/a | [Bundles: How bundles change][BUN] |
| B.8 | Submitting means accepting the terms of sale and choosing automatic or manual publication. | inform | n/a | [Build a bundle: publish][BB] |

[TR]: https://www.fab.com/o/technical-requirements
[AFF]: https://dev.epicgames.com/documentation/fab/asset-file-format-and-structure-requirements-in-fab
[UEFN]: https://dev.epicgames.com/documentation/fab/upload-unreal-editor-for-fortnite-source-to-fab
[PUB]: https://dev.epicgames.com/documentation/fab/publishing-assets-for-sale-or-free-download-in-fab
[LIC]: https://dev.epicgames.com/documentation/fab/licenses-and-pricing-in-fab
[BUN]: https://dev.epicgames.com/documentation/fab/bundles
[BB]: https://dev.epicgames.com/documentation/fab/build-and-publish-a-bundle
[DA]: https://www.fab.com/distribution-agreement
