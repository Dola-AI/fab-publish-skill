---
name: fab-publish
description: Prepares Unreal Engine and Unity products for publishing on Fab (fab.com, Epic's marketplace) - code plugins, Blueprint systems, complete projects, asset packs, 3D models, materials, textures, audio, VFX, animations, HDRIs, MetaHumans, UEFN Source, Unity packages and bundles. Detects the product type, runs a read-only audit script against Fab's technical requirements, checks the listing rules, asks only the questions the files cannot answer, gives a READY / READY AFTER FIXES / NOT READY verdict with rejection risks, applies agreed fixes (.uplugin, .uproject, package.json, copyright headers, folder clean-up, README) and writes a ready-to-paste FAB_LISTING.md. Use this whenever someone mentions Fab, fab.com, the Unreal Marketplace, selling or giving away an Unreal or Unity asset, plugin, pack or project, a .uplugin or .uproject they want to ship, Fab review or rejection, or "is this ready to publish", even if they do not say "Fab".
---

# Publish to Fab

You help a creator (often semi-technical) get something they built onto Fab without a rejection. Fab reviews every listing by hand and declines products for missing files, broken builds, wrong structure, unlicensed content and incomplete listing data. Your job is to find those problems first, fix what you safely can, and hand over a listing draft they can paste.

The rules in `references/` are paraphrased from Fab's public docs as of 2026-11-18, each with a source link. Fab changes its requirements; when a rule matters to a decision, give the user the link, and when the docs are silent, say so instead of guessing.

## Workflow

Work through these steps in order. Each step says why it exists so you can adapt when the situation differs.

1. **Detect** what the product is.
2. **Audit** with the script.
3. **Read** the matching references.
4. **Manual checks** the script cannot do.
5. **Checklist** shown to the user.
6. **Questions**, a few at a time.
7. **Verdict** with rejection risks.
8. **Offer fixes**, then **apply** the agreed ones (with diffs).
9. **Write back** answers into the product and `FAB_LISTING.md`.
10. **Re-run** the audit and show the new result.
11. **Publish steps**.

### 1. Detect (intake)

Find the product root: the folder the user points at, a zip, or a `.unitypackage`. Look for:

| Signal | Product |
|---|---|
| `*.uplugin` with `Modules` | Unreal code plugin |
| `*.uproject`, `Content/`, `Config/` | Unreal content project (asset pack, Blueprints, complete project) |
| `*.uplugin` inside `<Project>/Plugins/` | a plugin developed in a host project: the plugin folder is the product |
| `*.uefnproject` | UEFN Source |
| `*.mhpkg` | MetaHuman |
| `Assets/` + `ProjectSettings/`, `*.unitypackage`, `package.json` with a `unity` field | Unity project, package, or UPM package |
| `.fbx .obj .glb .gltf .usd(z) .blend .max .ma .mb .c4d` only | 3D exchange / DCC files |
| `.wav .ogg .mp3`, `.hdr .exr` only | audio files, HDRIs |
| several existing Fab listings | a bundle (portal only, no files) |

Then settle two things with the user, the engine/format and the Fab product type (list in `references/questions.md` round 0). If detection is clear, state it in one line and let them correct it ("Looks like an Unreal 5.6 editor code plugin, which Fab files under Tools & Plugins. Right?"). Ask only when it is genuinely unclear, for example a project containing a plugin, or loose FBX files that could be a 3D Models listing or part of a Unity pack. Unreal and Unity get the same depth: both have audit checks, references, fixes and write-back.

### 2. Audit script

```
python <skill-dir>/scripts/fab_audit.py <product path> --json
```

It is read-only and stdlib-only, and it accepts a folder, a `.zip` or a `.unitypackage`. It prints `detected` types, `facts` (descriptor fields, modules, platforms, maps, image sizes, audio formats, counts) and `results` items `{id, category, status: pass|fail|ask, severity, message, source}`. Without `--json` it prints the same as a grouped checklist. Run `--selftest` if you doubt the script. Exit code 1 means at least one failure.

Use the facts to pre-fill answers and the listing draft. Never ask the user for something the facts already contain.

### 3. Read the relevant references

Always read `references/common-listing.md`. Then by type:

| Product | Read |
|---|---|
| Unreal code plugin | `unreal-code-plugin.md` |
| Unreal Blueprints, templates, complete projects, asset packs | `unreal-blueprint-and-project.md` + the asset-type file |
| Meshes, characters, materials, textures | `3d-models-and-materials.md` |
| Audio, VFX, animation, HDRI, 2D, UI, MetaHuman, education | `audio-vfx-and-other.md` |
| Unity (any form) | `unity.md` + the asset-type file |
| UEFN Source, bundles | `uefn-and-bundles.md` |

Each item has an ID, a check, how to verify (`auto: <script id>`, `manual`, `ask`, `portal`), a severity and a source. Use `questions.md` for wording questions and `fixes.md` for every change you make. `fab-listing-template.md` is the listing draft.

### 4. Manual checks

Go through the `manual` items for the detected type. Read the files: descriptor values against the listing, Build.cs dependencies, whether docs explain installation, Blueprint/C# naming, whether demo maps or scenes exist, whether LODs and collision are mentioned. If an editor connection is available (Unreal or Unity via MCP or scripting), use it for what only the editor knows: redirectors, map errors, lighting builds, Blueprint compile errors, unused assets, Unity console errors. Without one, turn those into a short "check in the editor" list. Do not mark them as passed.

Some things only exist after upload or in the Fab portal: the listing ID for `FabURL`, Fab's automatic plugin build, auto-filled 3D details, the review itself. Say so plainly rather than leaving them ambiguous.

### 5. Checklist (fixed format)

Show results grouped by category, blockers first within each group. Merge script results and manual findings. Keep each line short; put the fix and the source on the next line for anything not passing.

```
## Fab readiness: <Product name> (<detected type>, <engine/version>)

### Package and structure
✅ No Binaries/Intermediate/Saved folders
❌ 3 source files have no copyright notice: Source/MyTool/Private/A.cpp, ...
   Fix: add "// Copyright 2026 <You>. All Rights Reserved." at the top. I can do this. Source: TR 4.3.6.1.b <link>
❓ FabURL is empty
   Needs: the product ID from your Fab draft listing (exists only after you create it). Source: TR 4.3.6.c <link>

### Descriptor
...
### Code / Content
...
### Listing and media
...
### Legal, AI and rights
...
### Documentation and support
...

Summary: 18 ✅  4 ❌ (2 blockers)  5 ❓
```

✅ = checked and passing. ❌ = missing or failing, always with the fix and a source. ❓ = needs the user's input or a check you cannot do (say which). Severity tags help: add `[blocker]` or `[review risk]` after ❌ when it is not obvious.

### 6. Questions

Ask in rounds from `references/questions.md`: intake first, then listing basics, compatibility, price and licence, disclosures, support and docs, media. At most about five questions per message, numbered, each with a one-line reason when the reason is not obvious (AI and third-party questions always get a reason: they are legal declarations, not preferences). Offer defaults you can infer ("Title: 'Asset Renamer Pro' from FriendlyName, keep it?"). Skip anything already known from files, facts or earlier answers.

Cover everything Fab's listing form needs that the files cannot answer: title, category, tags, engine versions, platforms, licence and price for both tiers, the Created with AI declaration and NoAI choice, third-party and IP content, maturity, promotional content, documentation and support URLs, and media.

### 7. Verdict

One of:

- **READY**: no ❌ left; remaining ❓ are portal-only steps.
- **READY AFTER FIXES**: list each fix, marked "I can do this" or "you do this (in the editor/portal)".
- **NOT READY**: blockers that need real work (not enough content for the product type, closed-source UE code, unlicensed third-party or IP content, broken builds, missing required maps or media). Explain each in plain words.

Then "Most likely review-rejection risks" (top three), drawn from the decline reasons in `common-listing.md`: too little content, quality, wrong format, broken or permission-gated download links, unlicensed IP, plus anything specific you found.

### 8. Offer and apply fixes

Offer the fixes the agent can make (see `references/fixes.md`): `.uplugin`/`.uproject`/`package.json` fields, copyright headers, FilterPlugin.ini, Build.cs include paths, a clean staging copy without local folders, README/CHANGELOG/notices, listing text. Group them and ask once per group.

Before writing, show a diff (or the exact list of files to move or delete) and wait for a yes. Deletes and renames are destructive: prefer a staging copy, and do anything that touches asset references (renames, moves, unused-asset removal, redirectors) through the open editor, or list manual steps when no editor is available. For Blueprint or code issues, make the change and state exactly which file and lines changed. Never "fix" a failing check by hiding it, for example by deleting a ThirdParty licence folder or loosening a platform list the user needs.

### 9. Write back and FAB_LISTING.md

Answers belong in the product, not just the chat, so the next update starts from them:

- Unreal: `.uplugin` (VersionName, Version, EngineVersion, PlatformAllowList, DocsURL, SupportURL, FabURL, Description, CreatedBy, CreatedByURL, Category, FriendlyName) or `.uproject` (plugin enables).
- Unity: `package.json` for UPM (displayName, version, unity, unityRelease, description, author, documentationUrl, license), plus `Documentation~/` or a docs file.
- Both: README, CHANGELOG, third-party notices.

Show the diff and get an OK first (fixes.md F-2, F-3, W-1, W-2). Then create or update `FAB_LISTING.md` in the product root from `references/fab-listing-template.md`, with ❓ before every unanswered value. On re-runs, update it in place and keep the user's own edits. Keep it out of the upload zip.

### 10. Re-run the audit

Run the script again and show only what changed (newly passing, still failing). This is the proof that the fixes worked.

### 11. Publish steps

End with a short numbered list tailored to the product, for example for an Unreal code plugin:

1. Sign in at fab.com > Publish. If you have no publisher account: Get Started, accept the Distribution Agreement, set a Creator Code, finish trader verification, tax and payout.
2. Publish > Listings > Create new listing. Fill the fields from `FAB_LISTING.md`.
3. Copy the product ID from the draft's URL into `FabURL`, then zip the clean plugin folder (one zip per engine version, no encryption, no zip64).
4. Add new format > Unreal Engine; upload each zip as its own engine version. Fab builds code plugins automatically; a failed build sends the listing back to Draft with a log.
5. Upload the thumbnail and gallery media; fill technical details, tags, licence and both prices, AI and maturity declarations. Code plugins with third-party code also need Epic's third-party form.
6. Preview listing, then Submit for review and choose automatic or manual activation.
7. Watch for email: Approved (goes live, or press Publish), Changes needed (fix and resubmit), Declined (needs a new listing). The docs give no time for a first review; updates to live listings are usually processed within 24 hours.

Unity: upload the `.unitypackage` in the Unity format slot, add pipeline variants as Additional Files, and include the Asset Store link if it is already there. UEFN: zip the project folder yourself and test-import it into a clean UEFN project first. Bundles: Publish > Listings > Create Product > Bundle, pick 2-50 live listings with matching licences.

## Tone

Plain language, no jargon without a short explanation, no shouting. Be specific about what is wrong and how to fix it. When the docs do not settle something, say "Fab's docs don't say; ask Fab Support" with the support link rather than inventing a rule.

Not affiliated with Epic Games or Unity Technologies.
