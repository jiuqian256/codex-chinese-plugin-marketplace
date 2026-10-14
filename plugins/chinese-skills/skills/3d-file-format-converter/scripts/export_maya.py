"""Run: mayapy export_maya.py <source.ma|source.mb> <output-folder>, or --config <UTF-8 JSON file>."""
import json
import os
import sys
import maya.standalone

if len(sys.argv) == 3 and sys.argv[1] == "--config":
    with open(sys.argv[2], encoding="utf-8") as config_file:
        config = json.load(config_file)
    source = os.path.abspath(config["source"])
    output_folder = os.path.abspath(config["output_folder"])
elif len(sys.argv) == 3:
    source, output_folder = map(os.path.abspath, sys.argv[1:])
else:
    raise SystemExit("Expected: <source> <output-folder> or --config <UTF-8 JSON file>")
base = os.path.splitext(os.path.basename(source))[0]
os.makedirs(output_folder, exist_ok=True)

maya.standalone.initialize(name="python")
try:
    import maya.cmds as cmds
    cmds.file(source, open=True, force=True, prompt=False)
    cmds.loadPlugin("objExport", quiet=True)
    cmds.loadPlugin("fbxmaya", quiet=True)
    cmds.file(os.path.join(output_folder, base + ".obj"), force=True, options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", type="OBJexport", exportAll=True)
    cmds.FBXResetExport()
    import maya.mel as mel
    fbx_path = os.path.join(output_folder, base + ".fbx").replace("\\", "/")
    mel.eval('FBXExport -f "{}"'.format(fbx_path.replace('"', '\\"')))
    print("CODEX_EXPORT_SUCCESS")
finally:
    maya.standalone.uninitialize()
