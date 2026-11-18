# Unreal Engine code plugins (.uplugin with C++ modules)

For products uploaded in the Unreal Engine format as a code plugin, usually listed under Tools & Plugins or Game Systems. Also read `common-listing.md`. Paraphrased from Fab's docs (snapshot 2026-11-18).

Fab builds code plugins itself, once per engine version you select, and ships its own binaries. Buyers install them as engine plugins (under `Engine/Plugins/Fab`), not as project plugins. Most rules below exist so that build succeeds on Epic's farm.

Verify: `auto: <id>` = `fab_audit.py` result id; `manual` = read files; `ask` = ask the user; `portal` = only in the Fab portal or after upload.

## Descriptor (.uplugin)

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| P.desc.1 | The .uplugin is valid JSON (no trailing commas, no comments). Invalid JSON fails the build with a parse error. | auto: uplugin.json | blocker | [Troubleshooting][TS] |
| P.desc.2 | `EngineVersion` is present and names one major version as `X.Y.0` (for example `5.6.0`). | auto: uplugin.engine_version | blocker | [TR 4.3.6.a][TR] |
| P.desc.3 | Every module has `PlatformAllowList` or `PlatformDenyList` (UE4: `WhitelistPlatforms`/`BlacklistPlatforms`). | auto: uplugin.platform_lists | blocker | [TR 4.3.6.b][TR], [Compile environment][ENV] |
| P.desc.4 | No retired platform names (HTML5 breaks the build). | auto: uplugin.platform_names | blocker | [Troubleshooting][TS] |
| P.desc.5 | `FabURL` is `com.epicgames.launcher://ue/Fab/product/<id>`, using the ID from the listing's portal URL. It can only be filled after the listing exists, so add it before the final file upload. | auto: uplugin.fab_url; portal | blocker | [TR 4.3.6.c][TR] |
| P.desc.6 | Module `Type` and `LoadingPhase` values are valid; each declared module has `Source/<Module>/<Module>.Build.cs`. | auto: uplugin.module_types, uplugin.loading_phase, uplugin.module_sources | blocker | [Troubleshooting][TS] |
| P.desc.7 | At least one C++ module (content may be included too). | auto: uplugin.has_module | blocker | [TR 4.3.6.1.c][TR] |
| P.desc.8 | `CanContainContent: true` when the plugin has a Content folder. | auto: uplugin.can_contain_content | blocker | [TR 4.3.6.1.c][TR] (links Epic's plugin docs on plugin content) |
| P.desc.9 | Listed plugin dependencies are engine-bundled only, never another user-made plugin. Experimental or beta ones are named in the description. | auto: uplugin.dependencies (asks); ask | blocker | [TR 4.3.6.d, 4.3.1.d][TR] |
| P.desc.10 | `FriendlyName`, `Description`, `VersionName`, `CreatedBy`, `CreatedByURL`, `DocsURL`, `SupportURL`, `Category` are filled and match the listing. | auto: uplugin.* (asks) | review risk | [TR 1.1.b, 4.3.8][TR] |

## Folder layout and files

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| P.dir.1 | Zip holds one plugin folder: `<Plugin>.uplugin`, `Source/`, and as needed `Config/`, `Content/`, `Resources/`. | auto: package.single, plugin.source | blocker | [TR 4.3.7.3.a][TR], [AFF: Code Plugins][AFF] |
| P.dir.2 | No `Binaries`, `Build`, `Intermediate`, `Saved` or other local folders. Leftover Binaries/Intermediate also cause farm errors. | auto: structure.local_folders | blocker | [TR 4.3.7.3.a][TR], [Troubleshooting][TS] |
| P.dir.3 | Any other top-level folder (such as `Docs`) is listed in `Config/FilterPlugin.ini`, or it is stripped. | auto: plugin.filterplugin | blocker | [TR 4.3.7.3.b][TR] |
| P.dir.4 | Every path, counted from the plugin folder name, is 170 characters or less. | auto: paths.length | blocker | [TR 4.3.7.3.c][TR] |
| P.dir.5 | Plugin folder name matches the .uplugin name and uses letters, digits, underscores. Renaming only by letter case can confuse Fab's storage; ask support if that happens. | auto: plugin.folder_name | review risk | [TR 4.3.7.1][TR], [Troubleshooting][TS] |
| P.dir.6 | Content names: English letters, digits, underscores; no vague names like Assets or NewFolder; consistent naming. | auto: naming.charset, naming.vague | review risk | [TR 4.3.7.1][TR] |
| P.dir.7 | No .uproject inside the plugin; an example project is offered as a separate download link in the technical information, depending on the plugin without containing it. | auto: plugin.no_project; ask | blocker | [TR 4.3.6.3][TR] |
| P.dir.8 | No .exe or .msi files. | auto: files.forbidden | blocker | [TR 4.3.6.1.e][TR] |
| P.dir.9 | Python scripts only under `Content/Python` (third-party under `Content/Python/Lib/site-packages`), commented, no hard-coded paths. | auto: python.location, text.absolute_paths | blocker | [AFF: Python Scripts][AFF] |

## Code

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| P.code.1 | Every .h/.cpp starts with a comment copyright notice naming the publisher or company and the publishing year, not the Epic template line. | auto: code.copyright, code.copyright_not_epic, code.copyright_year | blocker | [TR 4.3.6.1.b][TR] |
| P.code.2 | All UE-dependent code you wrote ships as source. Prebuilt libraries are allowed only for code that never touches UE headers, and they live in `Source/ThirdParty`. | auto: code.no_prebuilt_outside_thirdparty | blocker | [TR 4.3.6.1.a][TR] |
| P.code.3 | Third-party code sits in `Source/ThirdParty`, comes with proof of permission (licence file), and is declared on the listing and in Epic's third-party form. | auto: legal.thirdparty_licenses, legal.thirdparty_form | blocker | [TR 4.3.7.3.d, 4.2.5.b][TR] |
| P.code.4 | Include paths use `Path.Combine(ModuleDirectory, ...)`; no absolute paths in Build.cs. | auto: code.include_paths, code.build_abs_paths | blocker | [TR 4.3.6.2.e][TR] |
| P.code.5 | IWYU-friendly: `PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;` and each .cpp includes its own header first. | auto: code.iwyu; manual | review risk | [TR 4.3.6.2.c][TR], [Troubleshooting][TS] |
| P.code.6 | Compiles with no errors or meaningful warnings. Epic's Mac compilers treat some warnings as errors (shadowed variables, initialisation order); UFUNCTION/UPROPERTY exposed to Blueprints need a Category. | manual: run `RunUAT BuildPlugin` | blocker | [TR 4.3.6.2.a-b][TR], [Troubleshooting][TS] |
| P.code.7 | Works in binary (launcher) engine builds; source-built engine only for optional extras. | manual | blocker | [TR 4.3.1.i][TR] |
| P.code.8 | Adds editor features, integrates a third-party system, or exposes complex gameplay logic to Blueprints; most of it runs inside Unreal. | manual | blocker | [TR 4.3.6.1.d][TR] |
| P.code.9 | Has standalone value; paid extras through a licence or subscription are allowed only on top of that. | manual | review risk | [Code plugin functionality][FUNC] |
| P.code.10 | Blueprints shipped with the plugin are tidy, use clear names, no loose nodes, no errors or warnings. | manual (in editor) | review risk | [AFF: Tools & Plugins][AFF], [TR 4.3.5][TR] |

## Engine versions and listing

| ID | Check | Verify | Severity | Source |
|---|---|---|---|---|
| P.ver.1 | First submission includes a version for the latest engine release. | ask | blocker | [TR 4.2.2.b][TR] |
| P.ver.2 | One Project Version (separate zip, separate plugin folder) per supported engine version, even if only `EngineVersion` differs. | ask | blocker | [TR 4.2.2.d][TR], [Publishing: Unreal formats][PUB] |
| P.ver.3 | By default Epic builds against the three latest engine versions; older ones on request. At least one of the three latest must stay supported. | ask | review risk | [TR 4.3.6.2.d, 4.2.2.c][TR] |
| P.ver.4 | Supported target platforms on the listing match the platform allow lists. | ask | review risk | [TR 4.2.3.a][TR] |
| P.ver.5 | Documentation covers install and use (plugin installs to the engine, so say how to enable it per project). | auto: docs.present; ask | blocker | [TR 4.3.8][TR], [AFF: Tools & Plugins][AFF] |

## How to test the build locally (tell the user; the agent can run it if the engine is installed)

`Engine\Build\BatchFiles\RunUAT.bat BuildPlugin -Plugin="<abs path>\<Plugin>.uplugin" -Package="<output dir outside the plugin>" -Rocket` from each installed engine version, or Plugins window > Package. The output folder must be outside the engine directory. Do not zip the packaged output; zip the clean source folder. [TR 4.3.6.2.b][TR]

[TR]: https://www.fab.com/o/technical-requirements
[AFF]: https://dev.epicgames.com/documentation/fab/asset-file-format-and-structure-requirements-in-fab
[PUB]: https://dev.epicgames.com/documentation/fab/publishing-assets-for-sale-or-free-download-in-fab
[TS]: https://support.fab.com/s/article/Fab-Plugin-Compilation-Troubleshooting?language=en_US
[ENV]: https://support.fab.com/s/article/Fab-Plugin-Compilation-Environment?language=en_US
[FUNC]: https://support.fab.com/s/article/Engine-Code-Plugin-Functionality-info?language=en_US
