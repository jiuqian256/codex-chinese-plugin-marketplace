"""Load this tool with a plugin/version namespace; the manager imports entry as a file."""
import importlib
import importlib.util
import json
from pathlib import Path
import sys


def execute(doc):
    root=Path(__file__).resolve().parent
    manifest=json.loads((root/'plugin.json').read_text(encoding='utf-8'))
    namespace='shanze_'+manifest['id'].replace('-','_')+'_'+manifest['version'].replace('.','_').replace('-','_')
    if namespace not in sys.modules:
        spec=importlib.util.spec_from_file_location(namespace,root/'tool/__init__.py',submodule_search_locations=[str(root/'tool')])
        package=importlib.util.module_from_spec(spec)
        sys.modules[namespace]=package
        try:
            spec.loader.exec_module(package)
        except Exception:
            sys.modules.pop(namespace,None)
            raise
    return importlib.import_module(namespace+'.command').execute(doc)
