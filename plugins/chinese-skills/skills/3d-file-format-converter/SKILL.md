---
name: 3d-file-format-converter
description: 3D 文件识别与格式转换：识别真实 3D 文件格式，选择 Blender、Rhino 等工具，保留文件名导出 OBJ 或 FBX。 Identify the real type of a supplied 3D file, choose the optimal compatible 3D application, and convert it to user-selected same-basename target formats in a user-specified output folder. Use when a user asks to inspect a 3D file type, export or convert 3D scenes, retain the original base filename, select the best conversion software, choose OBJ/FBX or another output format, or needs help installing the required 3D application.
---

## 中文名称与用法

**中文名称：** 3D 文件识别与格式转换

**用途：** 识别真实 3D 文件格式，选择 Blender、Rhino 等工具，保留文件名导出 OBJ 或 FBX。

**调用示例：** 使用 $chinese-skills:3d-file-format-converter 把这个 3D 文件转换成 OBJ 和 FBX，保留原文件名。

文中的 `<SKILL_DIR>` 指本次加载的 SKILL.md 所在目录；从实际技能路径解析，不假定用户目录、操作系统或插件缓存版本。脚本接收的项目路径和输出路径仍使用当前任务的实际路径。


# 识别 3D 文件并转换格式

Identify the actual source format before selecting a converter. Preserve the source file and use the input filename's base name for every export.

## Workflow

1. **Identify the actual 3D file type first.** Verify the source exists, inspect its extension, first bytes, and recognizable header/embedded strings. Do not trust an extension alone. Report the detected format and relevant version/plugin clues before conversion.
   - `.max`: Compound File signature `D0 CF 11 E0 A1 B1 1A E1`; strings such as `Scene`, `ClassDirectory3`, Autodesk, V-Ray support a 3ds Max identification.
   - `.fbx`: begins with `Kaydara FBX Binary` (binary) or `; FBX` (ASCII).
   - `.obj`: text containing `v ` / `f ` records, normally with optional `.mtl`.
   - `.blend` (not `.Blende`): begins with `BLENDER`.
   - `.ma`: Maya ASCII text; `.mb`: Maya binary; `.3dm`: Rhino; `.stp`/`.step`: STEP; `.x_t`: Parasolid; `.c4d`: Cinema 4D.
   - `.3ds`: starts `4D 4D`; `.dae`: XML with `COLLADA`; `.gltf`: JSON containing `asset`; `.glb`: starts `67 6C 54 46` (`glTF`).
2. **Discover installed 3D software before choosing an application.** Never assume a drive letter, installation folder, or version. Run [find_3d_apps.ps1](scripts/find_3d_apps.ps1) before each conversion session. It searches PATH, environment variables, installed-program registry records, common folders on every mounted file-system drive, then every mounted drive by executable name. Record the discovered executable path and use that exact path for the job.

   Choose the optimal application based on the detected format and discovered executables:

   | Detected format | Preferred conversion application | Fallback |
   | --- | --- | --- |
   | 3ds Max `.max` | Autodesk 3ds Max / `3dsmaxbatch.exe` | None that reliably reads MAX |
   | Blender `.blend`, glTF/GLB, OBJ, DAE, 3DS | Blender | Assimp for straightforward mesh-only formats |
   | Maya `.ma` / `.mb` | Autodesk Maya | Blender only after a Maya export |
   | Cinema 4D `.c4d` | Maxon Cinema 4D | Ask for FBX export from Cinema 4D |
   | SketchUp `.skp` | SketchUp Pro | Blender import where supported |
   | Rhino `.3dm`, STEP `.stp`/`.step`, Parasolid `.x_t` | Rhino (imports and exports these CAD formats) | Ask for Rhino export if the installed Rhino edition lacks the importer |
   | Unknown/proprietary | The originating application's current version | Ask the user for origin/application if detection is inconclusive |

   Prefer the native application because it best preserves scene hierarchy, materials, animation, modifiers, and vendor-specific content. If several compatible versions are found, first choose a version that can open the source; prefer the newest compatible version, but retry another discovered version if scene or plug-in compatibility fails. Use Blender for formats it natively imports when a proprietary native application is unavailable. Clearly state when an export is mesh-only or loses unsupported data.
3. **Before exporting, confirm the target format.** If the user did not explicitly state it, ask: “需要输出 `.obj`、`.fbx`，还是两者都要？如果都不是，请告诉我需要的输出格式。” Do not begin exporting until the user answers. If they request another format, confirm the selected native application supports that exporter; otherwise explain the limitation and offer supported alternatives. Then ask for an output directory only if the user has not supplied one. Create it if needed. Never overwrite the source.
4. Use a **verified workflow** for the selected application and confirmed format(s):
   - `.max`: Use [export_max.ms](scripts/export_max.ms) with `3dsmaxbatch.exe`, passing absolute `sourceFile` and `outputFolder` values through `-mxsString`. Run without the 3ds Max UI; preserve the source `.max`. This is the preferred MAX workflow.
   - `.blend`: [export_blender.py](scripts/export_blender.py) with `blender --background --python ... -- <source> <output-folder>`.
   - `.ma`/`.mb`: [export_maya.py](scripts/export_maya.py) with `mayapy`; ensure Maya OBJ and FBX plug-ins are available.
   - `.3dm`, `.stp`/`.step`, `.x_t`: Use Rhino 8's `rhinocode.exe` script server with [export_rhino.py](scripts/export_rhino.py). Start Rhino once with `-_StartScriptServer`, write a UTF-8 JSON configuration (`source`, `output_folder`, and requested `formats`), set `RHINO_CONVERSION_CONFIG` before starting Rhino, then run `rhinocode script <script-path>`. The script uses `RhinoDoc.OpenHeadless()` and `doc.Export()`, so the source opens as a headless document rather than through UI macros.
   - `.c4d`: Use the discovered Cinema 4D installation's `c4dpy.exe` with [export_cinema4d.py](scripts/export_cinema4d.py). This is a verified no-GUI workflow for OBJ and FBX.

   The bundled scripts currently export OBJ and FBX. For another confirmed target format, use the selected application's native exporter and record its version-specific export settings. Do not generate an unrequested OBJ/FBX file.

   Do not substitute a generic converter for proprietary formats. Use literal paths in PowerShell; for source paths containing Chinese characters, use the JSON configuration method for Maya and Rhino.
5. Verify every requested export exists and is non-zero size. For OBJ, check geometry (`v` and `f` records); for FBX, check that it begins with `Kaydara FBX Binary` or is valid ASCII FBX. Use a format-appropriate header or application reopen check for other targets.

Use literal paths in PowerShell because paths can contain spaces and Chinese characters. Preserve the base filename exactly; only change its extension.

## Run with 3ds Max Batch

Run the bundled MAXScript without opening 3ds Max manually:

```powershell
& $maxBatch $scriptPath `
  -mxsString "sourceFile:E:\source\model.max" `
  -mxsString "outputFolder:D:\exports" `
  -listenerlog "D:\exports\max-export.log" -v 3
```

Use `quiet:true` / `#noPrompt` from [export_max.ms](scripts/export_max.ms). Keep the listener log, and validate both generated files before reporting success. If a specific scene stalls because of version or renderer plug-in incompatibility, report the failure with the log; do not change the normal MAX batch method for all other files.

This method was verified on an installed 3ds Max version for `3d66.com_21735570.max` and `3d66.com_23859123.max`. A particular MAX file can still stall during source-scene loading because of legacy renderer or plug-in compatibility; retry another discovered compatible version when available.

## Blender background batch

Use the verified Blender background invocation for `.blend`:

```powershell
& $blender --background --python '...\scripts\export_blender.py' -- 'E:\source\model.blend' 'D:\exports'
```

This was verified with an installed Blender version, producing OBJ, MTL, and binary FBX. [export_blender.py](scripts/export_blender.py) currently exports OBJ and FBX together; invoke it only after the user confirms both formats.

## Cinema 4D c4dpy batch

Use the `c4dpy.exe` found by the full software-discovery scan, not the GUI executable. It runs the matching installed Cinema 4D Python API as a headless process:

```powershell
& $c4dpy '...\scripts\export_cinema4d.py' 'H:\source\model.c4d' 'D:\exports'
```

[export_cinema4d.py](scripts/export_cinema4d.py) opens the `.c4d` with `LoadDocument` and saves OBJ/FBX through Cinema 4D's scene savers. Before using a newly discovered Cinema 4D version, inspect its registered scene-saver IDs and confirm its OBJ and FBX IDs; check each `SaveDocument` return value and fail the job if either is false.

This was verified on an installed Cinema 4D version with `蓝牙适配器TT54H_11_ID.c4d`, producing a geometric OBJ and binary FBX. Cinema 4D may write third-party plug-in warnings and may report an MTL export warning; report that material/texture data may be incomplete, but accept the result when OBJ geometry and FBX validation both pass. An earlier scene (`YPM005_13_场景-2.c4d`) exported FBX but its OBJ scene saver returned false; treat each source file independently.

## Maya mayapy batch

Use [export_maya.py](scripts/export_maya.py) with `mayapy` for `.ma` / `.mb`. For ASCII-only paths:

```powershell
& $mayapy '...\scripts\export_maya.py' 'E:\source\model.mb' 'D:\exports'
```

For source paths containing Chinese or other non-ASCII characters, create a UTF-8 JSON file and use the tested `--config` route instead of passing the source path on the `mayapy` command line:

```json
{"source":"H:\\模型\\model.mb","output_folder":"D:\\exports"}
```

```powershell
& $mayapy '...\scripts\export_maya.py' --config 'D:\exports\maya-job.json'
```

This was verified with an installed Maya version for a `.mb` scene. Missing V-Ray or old color-management settings can produce warnings and affect materials, but do not invalidate the geometry export when both output files verify.

## Rhino 8 headless batch

Use a discovered Rhino installation that provides both `rhinocode.exe` and `OpenHeadless` support, not `/runscript` macro quoting for Python execution. Rhino's official `rhinocode` CLI communicates with a running Rhino script server, while `OpenHeadless` and `Export` avoid UI document loading and export option dialogs. This was validated with a `.3dm` source exporting OBJ and FBX.

```powershell
$env:RHINO_CONVERSION_CONFIG = 'D:\exports\rhino-job.json'
Start-Process '<实际 Rhino 安装目录>
# Wait until `rhinocode list` reports an instance, then:
& '<实际 Rhino 安装目录>
```

Set `RHINO_CONVERSION_CONFIG` in the environment **before starting Rhino**, because the script server inherits its environment at launch. The JSON configuration must use UTF-8, for example: `{"source":"H:\\model.3dm","output_folder":"D:\\exports","formats":["obj","fbx"]}`. Validate every output file after `rhinocode` returns. If a discovered Rhino installation lacks `rhinocode` or `OpenHeadless`, select another discovered compatible installation or explain that a compatible Rhino installation is required.

The method was verified on an installed Rhino version with `端面检测.3dm`, producing OBJ and FBX successfully.

## Verified-result checks

For every conversion, do not rely on a process exit code alone. Require all requested files to exist and be non-zero length. For OBJ, require `v ` and `f ` records; for FBX, require the binary header `Kaydara FBX Binary` or a valid ASCII FBX header. Report companion `.mtl` files when an OBJ export creates them.

## Missing software: rapid installation guidance

If the chosen application is not installed, first state the detected format and why that application is optimal. Then give the official rapid-install route. Do not claim that a generic converter can reliably open a proprietary file.

For `.max`, explain that it is proprietary and cannot be reliably exported by ordinary OBJ/FBX converters. Give these concise options:

- Install **Autodesk 3ds Max** from the user's Autodesk Account, Autodesk Access, or the official [3ds Max product page](https://www.autodesk.com/products/3ds-max/overview). Sign in, install the current version, then rerun the conversion. Newer 3ds Max versions generally open older scenes.
- If the scene references V-Ray or another renderer/plugin, install the matching/current plugin too (for V-Ray, use the official [Chaos downloads page](https://www.chaos.com/download/build)). Geometry can often export without it, but materials, cameras, or lights may be incomplete.
- If installation is not possible, ask the user to open the scene in 3ds Max elsewhere and export OBJ/FBX, or provide the archive/texture files and a machine that has 3ds Max.

For Blender-compatible formats, direct the user to the official [Blender download page](https://www.blender.org/download/); install the current stable release, then rerun conversion. For other proprietary formats, direct the user to the original vendor's official download page and ask them to confirm installation before proceeding.

Do not download pirated software or bypass licenses. Before installing software, tell the user the official download route and any required account/license; follow their direction for the actual installation.

## Caveats

OBJ contains static mesh geometry, UVs, normals, and a companion MTL file but does not preserve animations, cameras, lights, hierarchy, or procedural modifiers. FBX preserves more scene data, subject to third-party plugins and exporter support. Mention missing external textures or V-Ray materials in the handoff when applicable.
