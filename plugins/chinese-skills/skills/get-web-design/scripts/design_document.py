"""Conservative measured tokens and the DESIGN.md format contract (Python 3.9)."""
import json
import re
from collections import Counter

DESIGN_SECTIONS = ['Overview', 'Colors', 'Typography', 'Layout', 'Elevation & Depth',
                   'Shapes', 'Components', "Do's and Don'ts"]


def dimension(value):
    return isinstance(value, str) and re.fullmatch(r'-?\d+(?:\.\d+)?(?:px|em|rem)', value) is not None


def color(value):
    return isinstance(value, str) and re.fullmatch(
        r'#(?:[\da-f]{3}|[\da-f]{4}|[\da-f]{6}|[\da-f]{8})|rgba?\(\s*[\d.,%\s/]+\)', value, re.I) is not None


def extract_design_tokens(raw_evidence=None):
    raw = (raw_evidence or {}).get('rows') or []
    rows = [row for row in raw if isinstance(row, dict) and not row.get('lowConfidence')]
    tokens, sources = {}, {}

    def typography(row):
        t = row.get('typography') or {}
        result = {}
        if isinstance(t.get('fontFamily'), str) and t['fontFamily'].strip():
            result['fontFamily'] = t['fontFamily']
        for key in ['fontSize', 'lineHeight', 'letterSpacing']:
            if dimension(t.get(key)):
                result[key] = t[key]
        weight = str(t.get('fontWeight', ''))
        if re.fullmatch(r'\d+(?:\.\d+)?', weight) and 1 <= float(weight) <= 1000:
            result['fontWeight'] = float(weight) if '.' in weight else int(weight)
        return result

    def representative(candidates):
        if not candidates:
            return None
        keys = [json.dumps([typography(r), r.get('color') or {}, r.get('box') or {}], sort_keys=True) for r in candidates]
        counts = Counter(keys)
        return candidates[max(range(len(keys)), key=lambda i: counts[keys[i]])]

    body = representative([r for r in rows if r.get('tagName') in ['body', 'p', 'li']])
    foreground = body or representative(rows)
    surface = representative([r for r in rows if r.get('tagName') == 'body'])
    colors = {}
    for name, row, key, role in [('primary', foreground, 'color', 'sampled foreground; not necessarily brand accent'),
                                 ('surface', surface, 'backgroundColor', 'body background; may be transparent')]:
        value = ((row or {}).get('color') or {}).get(key)
        if color(value):
            colors[name] = value
            sources['colors.' + name] = {'selector': row.get('selectorHint') or row.get('tagName'), 'role': role}
    if colors:
        tokens['colors'] = colors
    types = {}
    for tag in ['h1', 'h2', 'h3', 'p', 'label']:
        row = representative([r for r in rows if r.get('tagName') == tag and typography(r)])
        if row:
            name = 'body' if tag == 'p' else tag
            types[name] = typography(row)
            sources['typography.' + name] = {'selector': row.get('selectorHint') or tag, 'role': 'sampled ' + tag}
    if types:
        tokens['typography'] = types
    for group, properties in [('rounded', ['borderRadius']), ('spacing', ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'marginTop', 'marginRight', 'marginBottom', 'marginLeft'])]:
        values = list(dict.fromkeys((r.get('box') or {}).get(key) for r in rows for key in properties
                      if dimension((r.get('box') or {}).get(key)) and not r['box'][key].startswith('-')))
        if values:
            tokens[group] = {'sample-' + str(i + 1): value for i, value in enumerate(values[:12])}
    components = {}
    for role in ['button', 'input', 'link', 'card']:
        row = representative([r for r in rows if r.get('componentType') == role])
        if not row:
            continue
        component = {}
        for key, source, prop, check in [('backgroundColor', 'color', 'backgroundColor', color), ('textColor', 'color', 'color', color),
                                         ('rounded', 'box', 'borderRadius', dimension), ('padding', 'box', 'padding', dimension)]:
            value = (row.get(source) or {}).get(prop)
            if check(value):
                component[key] = value
        if component:
            components['sample-' + role] = component
            sources['components.sample-' + role] = {'selector': row.get('selectorHint') or row.get('tagName'), 'role': 'observed default state; variants unverified'}
    if components:
        tokens['components'] = components
    return {'tokens': tokens, 'sources': sources}


def build_design_frontmatter(hostname, tokens=None):
    data = {'name': (hostname or 'Unknown') + ' Design System', 'version': 'alpha',
            'description': 'Extracted visual reference. Tokens are measured samples; semantic roles require context. Unobserved values are omitted.', **(tokens or {})}

    def yaml(obj, indent=''):
        return '\n'.join(indent + key + ':\n' + yaml(value, indent + '  ') if isinstance(value, dict)
                         else indent + key + ': ' + json.dumps(value, ensure_ascii=False) for key, value in obj.items())
    return '---\n' + yaml(data) + '\n---'


def validate_design_body(body):
    headings = [m.strip() for m in re.findall(r'^## (.+)$', body, re.M)]
    if headings != DESIGN_SECTIONS or re.search(r'^(?:# |---\s*$|\s*```|\s*~~~)', body, re.M):
        raise ValueError('DESIGN.md structure invalid: expected the eight standard sections in order, without frontmatter or code fences. Regenerate the analysis.')
    if any(not section.strip() for section in re.split(r'^## .+$', body, flags=re.M)[1:]):
        raise ValueError('DESIGN.md contains an empty section. Regenerate the analysis.')
