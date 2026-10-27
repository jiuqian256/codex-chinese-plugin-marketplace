"""Build/check a Shanze plugin ZIP without executing it or publishing to a live server."""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import zipfile

sys.dont_write_bytecode=True


def safe_location(path):
    for parent in (path,*path.parents):
        if parent.is_symlink() or (parent.exists() and getattr(parent.stat(),'st_file_attributes',0)&0x400):
            raise ValueError('Path crosses a symlink or Junction: '+str(parent))


def registry_root(value):
    candidates=[Path(value)] if value else [Path.cwd(),Path.cwd()/'CompanyPluginManager']
    for path in candidates:
        if all((path/name).is_file() for name in ('README.md','CompanyPluginManager/pm_core.py','server/server.py','CompanyPluginManager/pm_updates.py')):
            return path.resolve()
    raise ValueError('Target registry source not found; provide --registry-root with README.md, CompanyPluginManager and server')


def build_source(source):
    safe_location(source)
    if not source.is_dir():raise ValueError('Source must be a directory')
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob('*')):
            relative=path.relative_to(source)
            if any(part in ('.git','.venv','__pycache__') for part in relative.parts):continue
            safe_location(path)
            if path.is_file():archive.write(path,relative.as_posix())
    return stream.getvalue()


def check(args):
    root=registry_root(args.registry_root)
    sys.path[:0]=[str(root/'CompanyPluginManager'),str(root/'server')]
    from pm_core import Client,inspect_package,validate_manifest,atomic_json
    from pm_updates import compare_versions
    from server import Registry
    output=Path(args.output).absolute() if args.output else None
    if args.source:
        if output is None:raise ValueError('--source requires --output')
        source=Path(args.source).absolute()
        safe_location(source);safe_location(output)
        if output.resolve().is_relative_to(source.resolve()):raise ValueError('ZIP output must be outside source directory')
        if output.exists():raise FileExistsError('Output already exists; use a new version/path: '+str(output))
        data=build_source(source)
        workspace=output.parent
    else:
        if output is not None:raise ValueError('--zip checks the existing file; omit --output')
        package=Path(args.zip).absolute();safe_location(package)
        data=package.read_bytes();workspace=package.parent
    safe_location(workspace)
    manifest=inspect_package(data)
    reserved={'sha256','size','path','restart_required'}&manifest.keys()
    if reserved:raise ValueError('Manifest contains runtime-generated fields: '+', '.join(sorted(reserved)))
    syntax_files=[]
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for entry in archive.infolist():
            if entry.filename.endswith('.py') and not entry.is_dir():
                ast.parse(archive.read(entry).decode('utf-8-sig'),filename=entry.filename)
                syntax_files.append(entry.filename)
    workspace.mkdir(parents=True,exist_ok=True)
    digest=hashlib.sha256(data).hexdigest()
    warnings=[]
    with tempfile.TemporaryDirectory(prefix='.shanze-preflight-',dir=workspace) as temp:
        temp=Path(temp)
        if args.catalog_url:
            catalog=Client({'server_url':args.catalog_url},temp/'catalog-reader').catalog()
        elif args.catalog:
            raw=json.loads(Path(args.catalog).read_text(encoding='utf-8-sig'))
            if raw.get('schema')!=1 or not isinstance(raw.get('plugins'),list):raise ValueError('Invalid catalogue JSON')
            catalog=raw['plugins']
            ids=set();commands=set()
            for item in catalog:
                validate_manifest(item)
                if item['id'] in ids or item['command_id'] in commands:raise ValueError('Catalogue contains duplicate plugin / command IDs')
                ids.add(item['id']);commands.add(item['command_id'])
        else:
            catalog=[];warnings.append('No current catalogue supplied; deployed ID conflicts and release history remain unverified.')
        for old in catalog:
            if old['id']!=manifest['id']:
                if old['command_id']==manifest['command_id']:raise ValueError('Command ID conflicts with deployed plugin: '+old['id'])
                continue
            if old['command_id']!=manifest['command_id'] or old.get('kind','python')!=manifest.get('kind','python'):
                raise ValueError('Existing plugin update cannot change command_id or kind')
            order=compare_versions(manifest['version'],old['version'])
            if order<0:raise ValueError('Version rollback rejected by development workflow')
            if order==0 and old.get('sha256')!=digest:raise ValueError('Same version has different content; increment version')
            if manifest.get('kind','python')=='native' and order>0:
                warnings.append('Native update requires C4D shutdown and administrator replacement; no in-session overwrite.')
        # Both publish and install run only against this temporary project-owned sandbox.
        registry=Registry(temp/'registry')
        atomic_json(registry.index_path,{'schema':1,'plugins':catalog})
        published=registry.publish(data)
        client=Client({'server_url':'http://127.0.0.1:1'},temp/'client',temp/'native',temp/'python-packages')
        installed=client.install(data,published,args.c4d_version)
        if not (Path(installed['path'])/manifest['entry']).is_file():raise ValueError('Sandbox installation is missing its entry')
    report={
        'status':'PREFLIGHT_PASSED','plugin':manifest,'sha256':digest,'bytes':len(data),
        'registry_root':str(root),'rules_sha256':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ('README.md','CompanyPluginManager/pm_core.py','server/server.py')},
        'catalog_conflicts_checked':bool(args.catalog or args.catalog_url),
        'historical_release_files_verified':False,'target_c4d_version':args.c4d_version,
        'real_registry_sandbox_publish':True,'real_client_sandbox_install':True,
        'python_syntax_files':syntax_files,'syntax_interpreter':sys.version.split()[0],
        'plugin_code_executed':False,'c4d_runtime_verified':False,'live_upload_performed':False,'warnings':warnings}
    if args.report:
        path=Path(args.report).absolute();safe_location(path)
        if path==output or (args.zip and path==Path(args.zip).absolute()) or (args.source and path.resolve().is_relative_to(Path(args.source).resolve())):
            raise ValueError('Report must not overwrite ZIP or enter plugin source')
        if path.exists():raise FileExistsError('Report already exists: '+str(path))
    if output:
        output.parent.mkdir(parents=True,exist_ok=True)
        with output.open('xb') as stream:stream.write(data)
        report['zip']=str(output)
    else:report['zip']=str(Path(args.zip).absolute())
    if args.report:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x',encoding='utf-8') as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--source');group.add_argument('--zip')
    parser.add_argument('--output');parser.add_argument('--registry-root')
    catalogs=parser.add_mutually_exclusive_group();catalogs.add_argument('--catalog');catalogs.add_argument('--catalog-url')
    parser.add_argument('--c4d-version',type=int,required=True);parser.add_argument('--report')
    args=parser.parse_args()
    try:result=check(args)
    except Exception as exc:
        print(json.dumps({'status':'PREFLIGHT_FAILED','error':str(exc)},ensure_ascii=False));return 2
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
