"""Run through Rhino 8 rhinocode. Set RHINO_CONVERSION_CONFIG to a UTF-8 JSON config path."""
import json
import os
import traceback
import Rhino

config_path = os.environ.get("RHINO_CONVERSION_CONFIG")
if not config_path:
    raise RuntimeError("Set RHINO_CONVERSION_CONFIG to a UTF-8 JSON file containing source and output_folder.")

with open(config_path, encoding="utf-8") as config_file:
    config = json.load(config_file)
source = os.path.abspath(config["source"])
output_folder = os.path.abspath(config["output_folder"])
formats = [item.lower().lstrip(".") for item in config.get("formats", ["obj", "fbx"])]
base = os.path.splitext(os.path.basename(source))[0]
os.makedirs(output_folder, exist_ok=True)

doc = Rhino.RhinoDoc.OpenHeadless(source)
if doc is None:
    raise RuntimeError("Rhino could not open source as a headless document: " + source)
try:
    results = {}
    for extension in formats:
        target = os.path.join(output_folder, base + "." + extension)
        results[extension] = doc.Export(target)
    if not all(results.values()):
        raise RuntimeError("Export failed: " + repr(results))
    print("CODEX_EXPORT_SUCCESS: " + repr(results))
finally:
    doc.Dispose()
