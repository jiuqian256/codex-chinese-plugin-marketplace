"""Validate the shareable marketplace without making API requests."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b')


def validate(root=ROOT):
    root = root.resolve()
    market = json.loads((root / '.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
    catalog = json.loads((root / 'SKILLS.json').read_text(encoding='utf-8'))
    assert market['name'] == 'chinese-skill-marketplace'
    assert len(market['plugins']) == 1
    entry = market['plugins'][0]
    path = entry['source']['path']
    assert entry['source']['source'] == 'local' and path.startswith('./')
    plugin = (root / path).resolve()
    assert plugin.is_relative_to(root) and plugin.is_dir()
    manifest = json.loads((plugin / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
    assert manifest['name'] == entry['name'] == 'chinese-skills'
    assert manifest['version'] == catalog['version'] == '1.0.2' and manifest['skills'] == './skills/'
    assert catalog['release_tag'] == 'v1.02'
    assert re.search(r'[\u4e00-\u9fff]', manifest['interface']['displayName'])
    names = {s['name'] for s in catalog['skills']}
    skills = plugin / 'skills'
    assert catalog['skill_count'] == len(names) == len(catalog['skills']) == 49
    assert names == {p.name for p in skills.iterdir() if p.is_dir()}
    for name in names:
        folder = skills / name
        content = (folder / 'SKILL.md').read_text(encoding='utf-8')
        match = re.match(r'\A---\n(.*?)\n---', content, re.S)
        assert match, name + ': invalid frontmatter'
        field = re.search(r'^name:\s*["\x27]?([a-z0-9-]+)["\x27]?\s*$', match[1], re.M)
        assert field and field[1] == name, name + ': name mismatch'
        assert re.search(r'^description:', match[1], re.M)
        assert re.search(r'[\u4e00-\u9fff]', match[1])
        agent = (folder / 'agents/openai.yaml').read_text(encoding='utf-8')
        assert 'display_name:' in agent and 'default_prompt:' in agent
        assert re.search(r'[\u4e00-\u9fff]', agent)
        assert '$chinese-skills:' + name in agent
        for file in folder.rglob('*'):
            assert not file.is_symlink() and file.resolve().is_relative_to(folder.resolve())
            if not file.is_file():
                continue
            assert file.suffix not in ('.pyc', '.pyo') and file.name != 'INSTALLATION.json'
            assert file.name != '.env' and not file.name.startswith('.env.')
            try:
                text = file.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                continue
            assert not TOKEN.search(text), str(file.relative_to(root)) + ': credential-shaped value'
            if file.name == 'SKILL.md':
                assert not re.search(r'C:[\\/]Users[\\/]Administrator', text), name + ': machine-specific path'
    assets = skills / 'galaxy-ui/assets/galaxy'
    assert len(list(assets.rglob('*.html'))) == 3802
    assert (assets / 'LICENSE').is_file()
    assert '<button' in (assets / 'Buttons/0x-Sarthak_hungry-penguin-30.html').read_text(encoding='utf-8')
    helper = (skills / 'image2-apinebula/scripts/image2_apinebula.py').read_text(encoding='utf-8')
    assert 'DEFAULT_API_KEY' not in helper and 'APINEBULA_API_KEY' in helper
    new_skills = {'ppt-master', 'frontend-slides', 'guizang-ppt-skill', 'huashu-design',
                  'html-ppt-studio', 'open-slide', 'dashi-ppt-skill', 'gorden-ppt-skill'}
    assert new_skills <= names
    for name in new_skills:
        folder = skills / name
        provenance = json.loads((folder / 'UPSTREAM.json').read_text(encoding='utf-8'))
        assert provenance['name'] == name and re.fullmatch(r'[a-f0-9]{40}', provenance['commit'])
        assert (folder / 'LICENSE').is_file(), name + ': missing upstream license'
    rea = skills / 'reverse-engineer-anything'
    provenance = json.loads((rea / 'UPSTREAM.json').read_text(encoding='utf-8'))
    assert provenance['repository'] == 'morluto/rea'
    assert provenance['commit'] == '3b79af28e80785afce9f5998d8f03289402a1847'
    assert (rea / 'LICENSE').is_file() and (rea / 'THIRD_PARTY_NOTICES.md').is_file()
    assert manifest['mcpServers'] == './.mcp.json'
    mcp = json.loads((plugin / '.mcp.json').read_text(encoding='utf-8'))['mcpServers']
    assert set(mcp) == {'rea'}
    assert mcp['rea']['command'] == 'node'
    assert mcp['rea']['args'][0] == '-e' and len(mcp['rea']['args']) == 2
    assert mcp['rea']['startup_timeout_sec'] >= 30
    launcher = mcp['rea']['args'][1]
    assert '${PLUGIN_ROOT}' not in launcher and 'process.platform' in launcher
    assert 'rea-agents@6.5.0' in launcher and '@latest' not in launcher
    assert (skills / 'gorden-ppt-skill/NOTICE.md').is_file()
    assert 'non-commercial' in (skills / 'gorden-ppt-skill/NOTICE.md').read_text(encoding='utf-8').lower()
    for name in ('create-slide', 'create-theme', 'current-slide', 'apply-comments', 'slide-authoring'):
        assert (skills / 'open-slide/references/upstream' / (name + '.md')).is_file()
    return {'status': 'PASS', 'plugins': 1, 'skills': len(names), 'galaxy_components': 3802,
            'portable_paths': True, 'credential_shape_scan': 'PASS'}


if __name__ == '__main__':
    print(json.dumps(validate(), ensure_ascii=False, indent=2))
