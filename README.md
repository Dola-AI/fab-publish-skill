# fab-publish: a Claude skill for publishing on Fab

By **[Dola AI](https://dolaai.pro)**, the AI assistant for Unreal Engine 5. Maintained by [@A-G-U-P-T-A](https://github.com/A-G-U-P-T-A).

A Claude Agent Skill that gets Unreal Engine and Unity products ready for [Fab](https://www.fab.com), Epic Games' marketplace. Point Claude at your plugin, project, asset pack or Unity package and it will:

1. detect what you built (code plugin, content project, UEFN Source, MetaHuman, Unity project/package/UPM, 3D files, audio, HDRI);
2. run a read-only audit script against Fab's technical requirements;
3. check the listing rules (media, licence, AI declaration, third-party content, docs, support);
4. ask only the questions your files cannot answer;
5. give a verdict (READY, READY AFTER FIXES or NOT READY) with the likeliest rejection reasons;
6. offer fixes it can make for you (descriptor fields, copyright headers, clean-up, README) and apply them after you agree;
7. write `FAB_LISTING.md`, a ready-to-paste draft of every listing field;
8. finish with the exact publish steps.

## Install

**Claude Code (plugin, recommended):**

```
/plugin marketplace add Dola-AI/fab-publish-skill
/plugin install fab-publish@dola-ai
```

Then just ask, e.g. "is my plugin ready for Fab?", or run `/fab-publish:fab-publish`.

**Claude Code (skill only):** copy `skills/fab-publish/` to `~/.claude/skills/fab-publish/` (all projects) or `<project>/.claude/skills/fab-publish/` (one project).

**Claude.ai / Claude desktop:** download `fab-publish.zip` from the [latest release](https://github.com/Dola-AI/fab-publish-skill/releases/latest) and upload it under Customize > Skills.

The audit script needs Python 3.8 or newer and nothing else.

## Example run

```
> I made an Unreal plugin in Plugins/AssetRenamer. Can I sell it on Fab?

Looks like an Unreal 5.6 editor code plugin (Tools & Plugins). Running the audit...

## Fab readiness: Asset Renamer (code plugin, UE 5.6)
### Package and structure
❌ Binaries/ and Intermediate/ must not be in the upload [blocker]
   Fix: I can build a clean copy in AssetRenamer_FabUpload/. Source: TR 4.3.7.3.a
### Descriptor
❌ Module "AssetRenamer" has no PlatformAllowList [blocker]
❓ FabURL is empty (fill after you create the draft listing)
...
Verdict: READY AFTER FIXES (3 I can do, 1 in the Fab portal)
```

You can also run the script on its own:

```
python skills/fab-publish/scripts/fab_audit.py path/to/MyPlugin          # checklist
python skills/fab-publish/scripts/fab_audit.py MyPlugin.zip --json       # machine-readable
python skills/fab-publish/scripts/fab_audit.py --selftest                # built-in tests
```

It never modifies files.

## Layout

```
skills/fab-publish/SKILL.md  workflow Claude follows
  references/                checklists per product type, question bank, fix recipes, listing template
  scripts/fab_audit.py       read-only audit (stdlib only)
  evals/                     test prompts
.claude-plugin/              plugin + marketplace manifests
```

## Sources and accuracy

The checklists paraphrase Fab's public documentation, technical requirements, help-center articles and the Unity Asset Store submission guidelines (which Fab applies to Unity products), as of **2026-11-18**. Every item links to its source. Requirements change, so check the linked page before relying on a rule for a business decision. This project does not reproduce Epic's or Unity's text.

**Not affiliated with, endorsed by or sponsored by Epic Games, Inc. or Unity Technologies.** Fab, Unreal Engine, UEFN and MetaHuman are trademarks of Epic Games; Unity is a trademark of Unity Technologies.

## Licence

MIT, see [LICENSE](LICENSE).

---

Made by [Dola AI](https://dolaai.pro) · [Docs](https://dolaai.pro/docs) · [Discord](https://discord.gg/2hna95rx3m) · Issues and pull requests welcome.
