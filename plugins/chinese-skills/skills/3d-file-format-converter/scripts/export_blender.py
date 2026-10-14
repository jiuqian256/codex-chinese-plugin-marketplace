"""Run: blender --background --python export_blender.py -- <source> <output-folder>"""
import bpy
import os
import sys

args = sys.argv[sys.argv.index("--") + 1 :]
if len(args) != 2:
    raise SystemExit("Expected: <source> <output-folder>")
source, output_folder = map(os.path.abspath, args)
base = os.path.splitext(os.path.basename(source))[0]
os.makedirs(output_folder, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=source)
bpy.ops.wm.obj_export(filepath=os.path.join(output_folder, base + ".obj"))
bpy.ops.export_scene.fbx(filepath=os.path.join(output_folder, base + ".fbx"), use_selection=False)
print("CODEX_EXPORT_SUCCESS")
