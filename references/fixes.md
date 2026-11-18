# Fixes and write-back recipes

Ground rules, because a broken project is worse than a rejected listing:

1. Show the user a diff (or an exact list of files to move or delete) and get a clear yes before writing. One yes covers the change shown, not later ones.
2. Never delete or rename in the user's working copy without that yes. Prefer working on a copy: for packaging fixes (removing Binaries, Saved and the like) offer to build a clean staging copy, for example `<Product>_FabUpload/`, and zip that, leaving the original alone.
3. Anything that changes asset references (renaming or moving .uasset/.umap files, deleting assets, fixing redirectors) goes through the engine. If Unreal or Unity is open and the agent can drive it (MCP, Python, editor scripting), do it there. Otherwise list the exact manual steps. Renaming .uasset files on disk breaks every reference to them.
4. Re-run `fab_audit.py` after every batch of fixes and show what changed.
5. Say exactly what changed: file, field, old value, new value.

## F-1 Remove local and build folders (Binaries, Intermediate, Saved, DerivedDataCache, Build, Library, Temp, .vs)

- Safe: these are regenerated. Still destructive, so confirm.
- Preferred: create a staging copy without them. Example (any OS, Python stdlib):
  `python -c "import shutil,sys; shutil.copytree(sys.argv[1], sys.argv[2], ignore=shutil.ignore_patterns('Binaries','Intermediate','Saved','DerivedDataCache','Build','.vs','.git'))" <src> <dst>`
- Plugins: keep `Source/ThirdParty/**/Binaries` or `lib` folders that hold third-party libraries; the ignore pattern above would drop any folder named Binaries, so check ThirdParty first and copy it back if needed.
- Before: `MyPlugin/{Binaries,Intermediate,Source,...}` After: `MyPlugin_FabUpload/MyPlugin/{Source,Config,Content,...}`.

## F-2 .uplugin edits (also the write-back target for answers)

Edit as JSON, keep the file's indentation (tabs in Epic's template), keep key order, and write without a BOM change. Fields:

| Field | Value | Note |
|---|---|---|
| `VersionName` / `Version` | "1.2.0" / integer bumped each release | |
| `FriendlyName`, `Description`, `Category` | from answers 1.1, 1.2, 0.2 | |
| `CreatedBy`, `CreatedByURL` | answer 5.2 | |
| `DocsURL`, `SupportURL` | answers 5.1, 5.2 | |
| `EngineVersion` | "5.6.0" | one engine version per zip; make one copy per version |
| `FabURL` | `com.epicgames.launcher://ue/Fab/product/<id>` | only after the listing exists; leave a reminder otherwise |
| `Modules[].PlatformAllowList` | e.g. `["Win64", "Mac", "Linux"]` | add to every module; for UE4 use `WhitelistPlatforms` |
| `CanContainContent` | true | if there is a Content folder |

Before:
```json
{ "FileVersion": 3, "Version": 1, "VersionName": "1.0", "FriendlyName": "MyTool",
  "Modules": [ { "Name": "MyTool", "Type": "Editor", "LoadingPhase": "Default" } ] }
```
After:
```json
{ "FileVersion": 3, "Version": 2, "VersionName": "1.1.0", "FriendlyName": "My Tool",
  "Description": "Batch-renames assets by rule.", "Category": "Editor", "CreatedBy": "Example Studio",
  "CreatedByURL": "https://example.com", "DocsURL": "https://example.com/mytool/docs",
  "SupportURL": "https://example.com/support", "EngineVersion": "5.6.0", "CanContainContent": false,
  "Modules": [ { "Name": "MyTool", "Type": "Editor", "LoadingPhase": "Default",
                 "PlatformAllowList": [ "Win64", "Mac", "Linux" ] } ] }
```
Remove trailing commas while there (the build farm rejects them). If the file uses the legacy `MarketplaceURL`, replace it with `FabURL` once the ID is known.

Per-engine-version copies: Fab wants one zip per engine version, each with its own plugin folder. Offer to produce `MyTool_5.5/MyTool`, `MyTool_5.6/MyTool`, ... from the staging copy, changing only `EngineVersion` unless code changes are needed.

## F-3 .uproject edits

- Set unused plugins to `"Enabled": false` (ask which are unused; never remove entries the project needs).
- Remove an empty `Modules` array only if there is no Source folder; a project with real C++ is not a content product: explain, do not delete code.
- `EngineAssociation` is informational; Fab uses the engine versions ticked on the listing.

## F-4 Copyright headers (.h/.cpp)

Insert or replace the first comment line, keeping everything else:

Before: `// Copyright Epic Games, Inc. All Rights Reserved.` or `// Fill out your copyright notice in the Description page of Project Settings.`
After: `// Copyright 2026 Example Studio. All Rights Reserved.`

Use the publisher or company name from answer 5.2 and the intended publishing year. Skip `Source/ThirdParty`. For Unity C# files this is optional; do not touch third-party scripts.

## F-5 FilterPlugin.ini

If the plugin has extra top-level folders (Docs, Examples), create or extend `Config/FilterPlugin.ini`:
```ini
[FilterPlugin]
/Docs/...
/Examples/...
```

## F-6 Build.cs include paths

Before: `PublicIncludePaths.Add("C:/Users/me/MyTool/Source/MyTool/Public");`
After: `PublicIncludePaths.Add(Path.Combine(ModuleDirectory, "Public"));` and `using System.IO;` at the top. Add `PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;` if missing. Then the user (or agent, if the engine is installed) runs `RunUAT BuildPlugin` to prove it still compiles.

## F-7 Folder structure (Unreal content)

- Single root under Content: move loose top-level folders into `Content/<Product>/`. Only in the editor (drag in the Content Browser, then Fix Up Redirectors on the root). Without the editor, give the steps; do not move .uasset files on disk.
- Delete `Content/Developers` and `Content/Collections` from the staging copy (not used by buyers).

## F-8 Renames to naming rules

Unreal assets: rename in the editor (Content Browser > Rename) so references update; then Fix Up Redirectors. Use type prefixes consistently if the project already does (SM_, T_, M_, MI_, BP_, ...). Folders: replace spaces and hyphens with underscores, give vague folders real names (Assets -> Meshes, NewFolder -> Props). Unity: rename in the Unity editor so .meta files and GUIDs follow; renaming on disk without the .meta breaks references.

## F-9 Unused and redirector assets

Only through the engine. Unreal: Fix Up Redirectors; for unused assets use the Reference Viewer/Size Map and confirm each delete with the user (Delete shows references; never force-delete). Unity: there is no safe automatic "unused" detection; list candidates and let the user decide.

## F-10 Unity fixes

- Namespaces: wrap classes in `namespace <Company>.<Product> { ... }`; update `using` lines in the package's own scripts. Ask before touching scripts other code depends on.
- Single root: move folders under `Assets/<Product>/` in the Unity editor.
- Source meshes (.blend etc.): export FBX in the DCC, move the source into `<Product>_Source.zip` outside or alongside.
- `Third-Party Notices.txt`: create from answer 4.2 (component, author, licence, link).

## W-1 Write-back: Unity package.json (UPM)

```json
{
  "name": "com.examplestudio.mytool",
  "displayName": "My Tool",
  "version": "1.1.0",
  "unity": "2022.3",
  "unityRelease": "0f1",
  "description": "Batch-renames assets by rule.",
  "author": { "name": "Example Studio", "url": "https://example.com" },
  "documentationUrl": "https://example.com/mytool/docs",
  "license": "Fab Standard License (see listing)"
}
```
Keep existing fields (dependencies, samples, keywords). Also add `Documentation~/index.md` if docs are missing, `CHANGELOG.md` and `LICENSE.md` (UPM convention).

## W-2 Write-back: README, CHANGELOG, LICENSE, notices (both engines)

- `README.md` (or `Docs/README.md` in a plugin, listed in FilterPlugin.ini): what it is, requirements (engine versions, platforms, pipelines, dependencies), install (Fab plugins install to the engine: enable it in Edit > Plugins; Unity: import the package), quick start, settings, support contact, version.
- `CHANGELOG.md`: `## 1.1.0 - 2026-11-18` plus bullet list. Reuse it for Fab's Changelog field on updates.
- Licence: products on Fab are licensed under the Fab EULA; do not add a custom licence that contradicts it. A `LICENSE` note pointing to the Fab listing is fine. Third-party components go in `ThirdPartyNotices.txt` (Unreal) or `Third-Party Notices.txt` (Unity).

## W-3 FAB_LISTING.md

Create or update `FAB_LISTING.md` in the product root from `fab-listing-template.md`, using answers, audit facts and descriptor fields. On re-runs, keep the user's own edits: update only fields whose source changed and replace ❓ markers that now have answers. It is a working file for the publisher, not product content: leave it out of the staging copy and the zip (Unreal), and keep it outside `Assets/` or out of the export (Unity).
