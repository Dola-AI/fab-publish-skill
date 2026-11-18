# Unreal Engine content projects: Blueprints, complete projects, content-only packs

For Unreal Engine format uploads that are not code plugins: asset packs, Blueprint systems, game templates, environments and complete projects (.uproject). Read `common-listing.md` too, and `3d-models-and-materials.md` or `audio-vfx-and-other.md` for the asset types inside. Paraphrased from Fab's docs (snapshot 2026-11-18).

Verify: `auto: <id>` = decidable from files (same id in the optional `fab_audit.py`); `manual` = read files or open the editor; `ask` = ask the user; `portal` = Fab portal only.

## Distribution method and versions

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| U.dist.1 | Distribution Method chosen: **Asset Pack** if buyers merge it into their own project, **Complete Project** if it is a standalone base or framework. | ask | blocker | [TR 4.2.4.a, c][TR] |
| U.dist.2 | Asset Packs have no Level Blueprint logic, no mandatory Config .ini settings and nothing that cannot be migrated to another project. | manual (editor), ask | blocker | [TR 4.2.4.b][TR] |
| U.dist.3 | A version for the latest engine release is included on first submission; at least one of the three latest stays supported. Content-only products can usually just tick new engine versions later. | ask | blocker | [TR 4.2.2][TR], [Publishing: Unreal formats][PUB] |
| U.dist.4 | Works in binary (launcher) engine builds. | manual | blocker | [TR 4.3.1.i][TR] |

## Project layout

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| U.dir.1 | Zip holds exactly one project: `<Project>.uproject`, `Config/`, `Content/`. | auto: package.single, project.config, project.content | blocker | [TR 4.2.1.a, 4.3.7.2.a][TR], [AFF: Content Product][AFF] |
| U.dir.2 | No `Binaries`, `Build`, `Intermediate`, `Saved`, `DerivedDataCache`, `Plugins` or unused folders. | auto: structure.local_folders | blocker | [TR 4.3.7.2.a][TR] |
| U.dir.3 | No C++: content products may not contain code modules or `Source/`. Code goes in a separate code-plugin listing. | auto: project.no_cpp | blocker | [AFF: Content Product][AFF] |
| U.dir.4 | `Content/` holds one folder only (the pack folder, named after the product) and no loose files. Fab's scanner checks this on upload. | auto: project.single_root, project.root_name | blocker | [TR 4.3.7.2.b][TR], [AFF: UE project requirements][AFF] |
| U.dir.5 | Inside the pack folder, assets are sorted into folders by type or set. | auto: project.sorted_folders; manual | review risk | [TR 4.3.7.2.c][TR] |
| U.dir.6 | Asset paths, counted from the pack folder name, are 140 characters or less. | auto: paths.length | blocker | [TR 4.3.7.2.d][TR] |
| U.dir.7 | Names: English letters, digits, underscores; descriptive and consistent; no Assets/NewFolder-style names. | auto: naming.charset, naming.vague; manual | review risk | [TR 4.3.7.1][TR] |
| U.dir.8 | No `Developers` or `Collections` folders under Content. | auto: content.dev_folders | blocker | [TR 4.3.7.2.a][TR] |
| U.dir.9 | No unused assets or folders. | manual (editor: Size Map / Reference Viewer) | blocker | [AFF: UE project requirements][AFF] |
| U.dir.10 | Redirectors are fixed up. | auto: content.redirectors (heuristic); manual | blocker | [TR 4.3.1.h][TR] |
| U.dir.11 | Plugins not used are `"Enabled": false` in the .uproject; required ones are available on Fab and named in the description. | auto: project.plugins (asks) | blocker | [TR 4.3.1.e-f][TR] |
| U.dir.12 | Python only under `Content/Python`. | auto: python.location | blocker | [AFF: Python Scripts][AFF] |
| U.dir.13 | Size under 15 GB without Saved and Intermediate, else contact Fab Support. | auto: package.size | review risk | [AFF: General][AFF] |

## Maps

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| U.map.1 | Visual products have an overview map with everything laid out (2D with UI/sprites, animations, archviz, characters, environments, materials, props, textures with materials, VFX, weapons). | auto: content.maps; manual | blocker | [AFF: Overview Maps][AFF], [TR 4.3.2.a][TR] |
| U.map.2 | Demo map present for Environments, and for Blueprints, Game Systems, Game Templates and Smart Assets unless they are only well-documented functions. | ask, manual | blocker | [AFF: Demo Map][AFF] |
| U.map.3 | Lighting built on every map. | manual (editor) | blocker | [TR 4.3.2.b][TR] |
| U.map.4 | No errors or meaningful warnings when the map loads or when Play-In-Editor starts. | manual (editor, Message Log) | blocker | [TR 4.3.2.c][TR] |
| U.map.5 | No z-fighting or overlapping polygons. | manual (editor) | review risk | [TR 4.3.2.d][TR] |

## Blueprints

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| U.bp.1 | Graphs are tidy and use functions to structure logic. | manual (editor) | review risk | [TR 4.3.5.a][TR] |
| U.bp.2 | Functions, variables and events have names that say what they do. | manual | review risk | [TR 4.3.5.b][TR] |
| U.bp.3 | No loose (unconnected) nodes unless commented as an example. | manual | review risk | [TR 4.3.5.c][TR] |
| U.bp.4 | Compile with no errors or meaningful warnings. | manual (editor: Compile all) | blocker | [TR 4.3.5.d][TR] |
| U.bp.5 | Listing has a demo download or a video URL in the long description showing it working. | ask | blocker | [TR 4.1.1.c][TR] |
| U.bp.6 | Large chunks of Epic Blueprints/code/materials are example-only, not the product. | manual | blocker | [TR 4.3.1.g][TR] |
| U.bp.7 | Game Systems, Templates, Smart Assets and Education products have thorough docs (video, written, Blueprint comments, in-level text or in-editor tutorial). | auto: docs.present; ask | blocker | [AFF: Game Systems, Smart Assets][AFF] |
| U.bp.8 | Minimum content: judged per product; Smart Assets need at least one unique asset (a drivable vehicle or a fully rigged and animated weapon for those types). | manual | review risk | [AFF: Smart Assets][AFF] |

## Content-wide

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| U.gen.1 | Assets are scaled to each other (humanoid 192 cm), face the same direction, Z up. | manual (editor) | review risk | [TR 2.3.1.a, 4.3.1.b][TR] |
| U.gen.2 | Nanite claimed only for UE 5.0+ meshes that are complex enough, with Nanite enabled by default. Lumen claims only for UE 5.0+. | manual | review risk | [AFF: Nanite, Lumen][AFF] |
| U.gen.3 | Substrate materials only with Substrate enabled in Project Settings. | manual | blocker | [TR 4.3.3.5.b][TR] |

## Editor-side checks the agent can run when Unreal is open

When an editor connection is available (for example through an MCP server or Python), prefer the editor: Fix Up Redirectors on the pack folder, run Map Check and a short PIE on each map and read the Message Log, Compile All Blueprints, Size Map on the pack for unused assets, and check that each map's lighting is built. Without the editor, list these as manual steps for the user.

[TR]: https://www.fab.com/o/technical-requirements
[AFF]: https://dev.epicgames.com/documentation/fab/asset-file-format-and-structure-requirements-in-fab
[PUB]: https://dev.epicgames.com/documentation/fab/publishing-assets-for-sale-or-free-download-in-fab
