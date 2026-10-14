"""Run with c4dpy: export_cinema4d.py <source.c4d> <output-folder>."""
import c4d
import os
import sys

if len(sys.argv) != 3:
    raise SystemExit("Expected: <source> <output-folder>")
source, output_folder = map(os.path.abspath, sys.argv[1:])
base = os.path.splitext(os.path.basename(source))[0]
os.makedirs(output_folder, exist_ok=True)

doc = c4d.documents.LoadDocument(source, c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS)
if doc is None:
    raise RuntimeError("Cinema 4D could not open source file")

def find_scene_saver(extension):
    extension = extension.lower()
    for plugin_id in range(1000000, 1100000):
        plugin = c4d.plugins.FindPlugin(plugin_id, c4d.PLUGINTYPE_SCENESAVER)
        if plugin and ("*." + extension) in plugin.GetName().lower():
            return plugin_id
    raise RuntimeError("No Cinema 4D scene saver found for *." + extension)

targets = {
    "obj": (os.path.join(output_folder, base + ".obj"), find_scene_saver("obj")),
    "fbx": (os.path.join(output_folder, base + ".fbx"), find_scene_saver("fbx")),
}
results = {}
for name, (path, exporter_id) in targets.items():
    results[name] = c4d.documents.SaveDocument(doc, path, c4d.SAVEDOCUMENTFLAGS_NONE, exporter_id)
if not all(results.values()):
    raise RuntimeError("Cinema 4D export failed: " + repr(results))
print("CODEX_EXPORT_SUCCESS: " + repr(results))
