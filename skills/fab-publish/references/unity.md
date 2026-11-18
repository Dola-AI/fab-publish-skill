# Unity products (.unitypackage, Unity project, UPM package)

Fab requires Unity products to meet the Unity Asset Store Submission Guidelines, plus Fab's own listing rules. Read `common-listing.md` too, and the asset-type reference (`3d-models-and-materials.md`, `audio-vfx-and-other.md`). Paraphrased from Fab's docs and Unity's guidelines (snapshot 2026-11-18; Unity's page was updated 2026-10-23).

Upload format: a `.unitypackage` (or `.unitypackage.gz`) in the Unity format slot. Extra render-pipeline variants can go as a zip under Additional Files. [Publishing: Unity formats][PUB]

## Fab-specific

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| Y.fab.1 | Meets the Unity Asset Store Submission Guidelines. | this file | blocker | [TR 7.1.a][TR] |
| Y.fab.2 | Dependencies are stated in the description; content hosted elsewhere (GitHub, Drive, Dropbox) is linked on the product page. | ask | blocker | [TR 7.2.a][TR] |
| Y.fab.3 | Already on the Unity Asset Store? Give that link when submitting, and keep the Fab files roughly the same as the Asset Store ones. | ask | blocker | [AFF: Unity][AFF] |
| Y.fab.4 | Size within the Asset Store limit: 6 GB, or 700 MB for UPM. | auto: package.size | blocker | [AFF: File Format][AFF], [Unity 1.1.e][UAS] |

## Structure

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| Y.dir.1 | Everything sits under one root folder in `Assets/`, except Unity special folders (Gizmos, Editor Default Resources, StreamingAssets, Plugins, Standard Assets). | auto: unity.root | blocker | [Unity 2.1.a][UAS] |
| Y.dir.2 | Folders sorted and named by content type (Meshes, Materials, Scripts...). | auto: naming.vague; manual | review risk | [Unity 2.1.b][UAS] |
| Y.dir.3 | No duplicate, unused or redundant files. | manual | review risk | [Unity 2.1.c][UAS] |
| Y.dir.4 | Nothing inside an `AssetStoreTools` folder (it is removed on upload). | auto: unity.assetstoretools | blocker | [Unity 2.1.d][UAS] |
| Y.dir.5 | Paths under 150 characters, measured from `Assets/` (UPM: from the package folder name). | auto: unity.path_length | blocker | [Unity 2.1.e][UAS] |
| Y.dir.6 | Every asset has its .meta file; no orphan .meta files. | auto: unity.meta_files | review risk | [Unity 5.2.d][UAS] |
| Y.dir.7 | No nested .unitypackage or archives that hide the content (allowed: settings, pipeline variants, add-ons). Zips only for non-Unity source files, with "source" in the name. | auto: unity.nested_packages, unity.zip_naming | blocker | [Unity 2.2][UAS] |
| Y.dir.8 | No executables (.exe, .apk). | auto: files.forbidden | blocker | [Unity 1.5.a][UAS], [TR 2.2][TR] |
| Y.dir.9 | Built with Unity 2022.3 or newer; packages for Unity 6.5+ support URP or HDRP. | auto: unity.version; ask | blocker | [Unity 1.3][UAS] |

## Code and editor scripts

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| Y.code.1 | All code in your own namespace, never `Unity*`/`UnityEngine`/`UnityEditor` or other trademarks. | auto: unity.namespaces, unity.namespace_trademark | blocker | [Unity 2.5.a][UAS] |
| Y.code.2 | No errors or warnings from the package after setup; known engine-bug warnings disclosed. No obsolete-API warnings on the latest supported editor. | manual (open in Unity) | blocker | [Unity 1.1.b, 2.5.i][UAS] |
| Y.code.3 | Readable, consistently named code; no reflection into Unity internal APIs. | manual | review risk | [Unity 2.5.d-g][UAS] |
| Y.code.4 | Works with Domain Reload disabled (required from Unity 6.6). | manual | blocker | [Unity 2.5.h][UAS] |
| Y.code.5 | Menus under an existing menu (Window/...) or Tools; no auto-opening websites; InitializeOnLoad only for real setup; no adding or removing other packages. | manual | blocker | [Unity 2.5.1][UAS] |
| Y.code.6 | API keys never stored where they end up in builds; third-party API terms and costs at the top of the description; analytics opt-in. | manual, ask | blocker | [Unity 1.5.b-e][UAS] |
| Y.code.7 | No DRM, time limits, registration walls or artificial limits (SaaS SDK exceptions apply); no watermarks. | manual | blocker | [Unity 1.4][UAS] |
| Y.code.8 | AI/MCP features use project data only for the disclosed feature, never to train models without consent, and do not slow the editor. | ask | blocker | [Unity 1.1.j-l][UAS] |
| Y.code.9 | Android support targets 64-bit. | ask | blocker | [Unity 2.5.b][UAS] |
| Y.code.10 | Assembly definition files are valid JSON and have scripts. | auto: unity.asmdef_json | blocker | [Unity 5.2.a-b][UAS] |

## Art, audio and scenes

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| Y.art.1 | 3D, 2D, VFX, Animation and Template products include a demo scene; tools that process files include sample files. | auto: unity.demo_scene | blocker | [Unity 1.1.f][UAS] |
| Y.art.2 | Meshes are .fbx, .dae, .abc or .obj; source files (Blender etc.) only in a zip named with "source". | auto: unity.mesh_formats | blocker | [Unity 2.4.a, 2.2.b][UAS] |
| Y.art.3 | Prefabs at position/rotation 0 and scale 1; +Z forward; 1 unit = 1 m; sensible pivots; colliders on static models; LOD Groups set up. | manual (Unity) | review risk | [Unity 2.4.d-j][UAS] |
| Y.art.4 | Meshes have materials and prefabs; scans and AI meshes are retopologised and editable. | manual | review risk | [Unity 2.4.b, g][UAS] |
| Y.art.5 | Textures lossless (.png/.tga/.psd), power of two where it fits, normal maps flagged, PBR sets complete, tiling seamless. | auto: unity.lossless_images, textures.power_of_two; manual | review risk | [Unity 2.4.3][UAS] |
| Y.art.6 | Animations sliced, uniquely named, smooth; humanoids mapped to Unity Humanoid or disclosed; animation products have a video. | manual, ask | blocker | [Unity 2.4.1][UAS] |
| Y.art.7 | Audio products: preview in the media, lossless files (.wav/.aiff/.flac), peaks no higher than -0.3 dB, SFX trimmed and sliced. | auto: audio.lossless, audio.peak; ask | blocker | [Unity 2.7][UAS] |
| Y.art.8 | No genitalia; characters adequately covered. | manual | blocker | [Unity 2.4.l][UAS] |
| Y.art.9 | AI-made content: no human-effort words like "hand painted" or "drawn"; not mass-produced lookalikes. | ask | blocker | [Unity 1.6][UAS] |

## Docs, legal, description

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| Y.doc.1 | Docs included when there is code, shaders, settings or setup (.txt/.md/.pdf/.html/.rtf; videos as links only). Offline docs strongly recommended. | auto: docs.present | blocker | [Unity 2.3][UAS] |
| Y.doc.2 | A `Third-Party Notices.txt` lists third-party components and their licences, and the description says which components are used under which licence. | auto: legal.third_party_notices; ask | blocker | [Unity 1.2.a][UAS] |
| Y.doc.3 | No licences that force open-sourcing or attribution in buyers' products (GPL, LGPL, attribution-required CC or Apache). | auto: legal.copyleft; ask | blocker | [Unity 1.2.b][UAS], [DA s.3c][DA] |
| Y.doc.4 | Description lists counts and technical specs (polycount, texture sizes, maps, render pipelines, audio sample rate/bit depth/length) and any limits. | ask | review risk | [Unity 3.1][UAS] |

## UPM packages (package.json)

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| Y.upm.1 | Manifest has `name`, `displayName`, `version`, `unity`, `unityRelease`, `author`, `description`. | auto: upm.required_fields | blocker | [Unity 5.2.e][UAS] |
| Y.upm.2 | `name` is reverse-domain lowercase and relevant; `version` is semver; `unity`/`unityRelease` match real compatibility; `author` is the publisher name. | auto: upm.name, upm.semver, unity.version | blocker | [Unity 5.2.f-i][UAS] |
| Y.upm.3 | Dependencies only on Unity packages or packages in the same product. | auto: upm.dependencies | blocker | [Unity 5.2.c][UAS] |
| Y.upm.4 | `documentationUrl`, `license`, `CHANGELOG.md`, `Documentation~/`, `LICENSE.md` present (Unity package layout conventions). | auto: upm.* | recommended | [Unity 2.3][UAS] |

[TR]: https://www.fab.com/o/technical-requirements
[AFF]: https://dev.epicgames.com/documentation/fab/asset-file-format-and-structure-requirements-in-fab
[PUB]: https://dev.epicgames.com/documentation/fab/publishing-assets-for-sale-or-free-download-in-fab
[UAS]: https://assetstore.unity.com/publishing/submission-guidelines
[DA]: https://www.fab.com/distribution-agreement
