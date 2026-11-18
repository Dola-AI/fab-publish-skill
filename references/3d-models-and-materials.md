# 3D models, characters, materials and textures

Covers 3D Models (props, characters, vehicles, weapons) and Material & Textures, in any format: Unreal, UEFN, Unity, exchange formats (FBX, OBJ, GLB, GLTF, USD, USDZ) and DCC files (Blender, Maya, 3ds Max, Cinema 4D). Also read `common-listing.md` and the engine reference (`unreal-blueprint-and-project.md`, `unity.md`, `uefn-and-bundles.md`). Paraphrased from Fab's docs (snapshot 2026-11-18).

## Exchange and DCC formats

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| M.fmt.1 | Each format upload contains only files of that format (a zip of several FBX is fine; FBX plus Blend in one upload is not). Upload each format separately. | auto: dcc.one_format | blocker | [TR 2.1][TR] |
| M.fmt.2 | Supported: USDZ, USD, OBJ, GLTF, GLB, FBX; DCC: Maya, Cinema 4D, Blender, 3ds Max. | auto: detection | blocker | [TR 2.1.a-b][TR], [Formats table][AFF] |
| M.fmt.3 | Texture and material references resolve inside the package; no absolute paths in .obj/.mtl/.gltf. | auto: dcc.references, text.absolute_paths | blocker | [TR 2.3.2.1.a][TR] |
| M.fmt.4 | Scale relative to a 192 cm humanoid. | manual (open in a DCC) | review risk | [TR 2.3.1.a][TR] |
| M.fmt.5 | No visual defects. Fab auto-fills vertex/face/texture counts for exchange formats and Blender; check them after upload. | manual; portal | blocker | [TR 2.3.2.1.a][TR], [Publishing: Product details][PUB] |

## Minimum content (Unreal products; Fab applies similar judgement elsewhere)

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| M.min.1 | Props: realistic/photogrammetry 1 unique model as an Asset Pack (5 recommended); simple stylized about 25; firearms 1 fully rigged and animated; vehicle static meshes 5 with interior and exterior; vehicle skeletal mesh 1 rigged with interior and exterior. | manual, ask | blocker | [AFF: Props][AFF] |
| M.min.2 | Characters: 1 game-ready full character (or 5 arms-only for first person), rigged to the Epic skeleton, with a full Control Rig, or with its own animation set (at least idle, jump, walk, run, plus genre-expected moves). | manual, ask | blocker | [AFF: Characters][AFF] |
| M.min.3 | Materials & Textures: at least 1 unique material, plus an overview map. | manual | blocker | [AFF: Materials & Textures][AFF] |
| M.min.4 | Not enough content is the top decline reason. | manual | review risk | [Declined][DECL] |

## Meshes (Unreal)

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| M.mesh.1 | Modular kits: pivots placed for clean assembly and pieces snap on a grid. | manual (editor) | review risk | [TR 4.3.3.2.a-b][TR] |
| M.mesh.2 | Lightmap UVs have no overlaps or wrapping; Lightmap Coordinate Index is not 0 (unless only used by particles). | manual (editor) | blocker | [TR 4.3.3.2.c, g][TR] |
| M.mesh.3 | No material defects, visible seams or lightmap problems. | manual | blocker | [TR 4.3.3.2.d][TR] |
| M.mesh.4 | Collision where it makes sense. | manual | review risk | [TR 4.3.3.2.e][TR] |
| M.mesh.5 | LODs used properly, and the description says which LODs are included (even "none"). | ask | blocker | [TR 4.3.3.2.f][TR] |

## Characters and animation

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| M.chr.1 | Skeletal meshes are scaled to the Epic or MetaHuman skeleton. | manual | blocker | [TR 4.3.3.4.a][TR] |
| M.chr.2 | Humanoids are rigged to the Epic or MetaHuman skeleton, or ship a scaled custom skeleton with all needed animations. | ask, manual | blocker | [TR 4.3.3.4.c][TR] |
| M.chr.3 | Epic/MetaHuman rigs keep bone names, IK bones unweighted in place, joint orientations unchanged, A-pose; extra bones or sockets are documented on the product page. Include the Third Person template animations in the overview map as proof. | manual | blocker | [TR 4.3.3.4.d][TR], [AFF: Characters][AFF] |
| M.chr.4 | Full range of motion without defects; Physics Assets cover the mesh and simulate sensibly. | manual | review risk | [TR 4.3.3.4.b, e-f][TR] |
| M.chr.5 | Non-Epic skeletons ship their own scaled skeleton plus animations, or a full Control Rig. | manual | blocker | [TR 4.3.3.3.b][TR] |

## Textures and materials

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| M.tex.1 | No texture over 16384 px on a side (UEFN: 8192, 4096 or less recommended). | auto: textures.max_size (loose image files); manual for .uasset | blocker | [TR 4.3.3.1.c, 6.3.3.1.c][TR] |
| M.tex.2 | Power-of-two sizes where mips are needed (1024x512 and so on). | auto: textures.power_of_two | recommended | [TR 4.3.3.1.b][TR] |
| M.tex.3 | Highest sensible resolution provided; extra resolutions allowed. | manual | recommended | [TR 4.3.3.1.a][TR] |
| M.tex.4 | Material instances used where possible. | manual (editor) | review risk | [TR 4.3.3.5.a][TR] |
| M.tex.5 | Substrate materials only if Substrate is enabled in the project. | manual | blocker | [TR 4.3.3.5.b][TR] |

## Rights checks that matter most for 3D

Photogrammetry and scans: who owns the scanned object (brands, artworks, buildings with trademarks)? Megascans cannot be repackaged. AI-generated meshes or textures need the Created with AI flag; Unity additionally expects scans and AI meshes to be retopologised and editable. See `common-listing.md` C.ip and C.ai, and `unity.md` Y.art.

[TR]: https://www.fab.com/o/technical-requirements
[AFF]: https://dev.epicgames.com/documentation/fab/asset-file-format-and-structure-requirements-in-fab
[PUB]: https://dev.epicgames.com/documentation/fab/publishing-assets-for-sale-or-free-download-in-fab
[DECL]: https://support.fab.com/s/article/Why-was-the-submission-declined?language=en_US
