#!/usr/bin/env python3
"""Regenerate standalone SVG diagrams from diagrams.json (requires Graphviz dot)."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import json
import subprocess
import textwrap
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(__file__).with_name('diagrams.json')
SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)


def quote(value):
    return json.dumps(value, ensure_ascii=False)


def wrapped(label, width=22):
    return '\\n'.join(textwrap.wrap(label, width, break_long_words=False, break_on_hyphens=False))


def dot_source(diagram, direction):
    lines = [
        'digraph {',
        f'graph [rankdir={direction}, bgcolor="#fcfcfa", pad="0.25", '
        'nodesep="0.3", ranksep="0.45", compound=true, outputorder=edgesfirst];',
        'node [shape=box, style="rounded,filled", fillcolor="#edf2ef", '
        'color="#8ba49b", fontcolor="#243d36", fontname="Georgia", '
        'fontsize=18, margin="0.2,0.14", penwidth=1.2];',
        'edge [color="#59786d", fontcolor="#405b50", fontname="Georgia", '
        'fontsize=15, arrowsize=0.7, penwidth=1.3];',
    ]
    nodes = {node['id']: node for node in diagram['nodes']}
    groups = {group['label']: (i, group) for i, group in enumerate(diagram['groups'])}
    outgoing = {edge['from'] for edge in diagram['edges']}
    for key, node in nodes.items():
        label = quote(wrapped(node['label'])).replace('\\\\n', '\\n')
        attributes = [f'label={label}']
        if node['shape'] == 'decision':
            attributes += ['shape=diamond', 'style=filled', 'fillcolor="#f5eddc"', 'color="#ae9766"']
        elif key not in outgoing:
            attributes += ['fillcolor="#dcebe3"', 'color="#527969"', 'penwidth=1.6']
        lines.append(f'{quote(key)} [{", ".join(attributes)}];')
    for i, group in enumerate(diagram['groups']):
        if not group['nodes']:
            raise ValueError(f'Empty group in {diagram["file"]}')
        label = quote(wrapped(group['label'], 35)).replace('\\\\n', '\\n')
        lines += [f'subgraph cluster_{i} {{',
                  f'graph [label={label}, fontname="Georgia", fontsize=18, '
                  'fontcolor="#405b50", color="#c6d2cb", style=rounded, margin=18];']
        lines += [quote(key) + ';' for key in group['nodes']]
        lines.append('}')
    for edge in diagram['edges']:
        attrs = []
        endpoints = []
        for side, attr in [('from', 'ltail'), ('to', 'lhead')]:
            key = edge[side]
            if key not in nodes:
                i, group = groups[key]
                key = group['nodes'][0]
                attrs.append(f'{attr}=cluster_{i}')
            endpoints.append(quote(key))
        if edge['label']:
            label = quote(wrapped(edge['label'], 18)).replace('\\\\n', '\\n')
            attrs.append(f'label={label}')
        if edge['dashed']:
            attrs.append('style=dashed')
        if not edge.get('arrow', True):
            attrs.append('dir=none')
        lines.append(f'{endpoints[0]} -> {endpoints[1]} [{", ".join(attrs)}];')
    return '\n'.join(lines + ['}'])


def render(diagram):
    candidates = []
    for direction in ('TB', 'LR'):
        result = subprocess.run(['dot', '-Tsvg'], input=dot_source(diagram, direction),
                                text=True, capture_output=True, check=True)
        tree = ET.fromstring(result.stdout)
        _, _, width, height = map(float, tree.attrib['viewBox'].split())
        # Favor legibility at article width; use height as the tie breaker.
        score = max(1, width / 660) ** 3 * height + max(0, width - 660) * 5
        candidates.append((score, tree))
    tree = min(candidates, key=lambda item: item[0])[1]
    tree.set('role', 'img')
    tree.set('aria-labelledby', 'title description')
    title = ET.Element(f'{{{SVG}}}title', {'id': 'title'})
    title.text = diagram['title']
    labels = {node['id']: node['label'] for node in diagram['nodes']}
    labels.update({group['label']: group['label'] for group in diagram['groups']})
    relationships = []
    for edge in diagram['edges']:
        connector = ' relates to ' if not edge.get('arrow', True) else ' leads to '
        annotation = f' ({edge["label"]})' if edge['label'] else ''
        if edge['dashed']:
            annotation += ' (dashed connection)'
        relationships.append(labels[edge['from']] + connector + labels[edge['to']] + annotation + '.')
    for group in diagram['groups']:
        relationships.append(group['label'] + ': ' + ', '.join(labels[key] for key in group['nodes']) + '.')
    description = ET.Element(f'{{{SVG}}}desc', {'id': 'description'})
    description.text = ' '.join(relationships)
    tree.insert(0, title)
    tree.insert(1, description)
    # Graphviz's internal titles only repeat node IDs and add distracting tooltips.
    for group in tree.iter(f'{{{SVG}}}g'):
        for child in list(group):
            if child.tag == f'{{{SVG}}}title':
                group.remove(child)
    destination = ROOT / diagram['file']
    destination.write_text(ET.tostring(tree, encoding='unicode') + '\n')
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', help='Render only image paths containing this text')
    args = parser.parse_args()
    diagrams = json.loads(MANIFEST.read_text())
    if args.only:
        diagrams = [diagram for diagram in diagrams if args.only in diagram['file']]
    with ThreadPoolExecutor(max_workers=8) as executor:
        paths = list(executor.map(render, diagrams))
    print(f'Rendered {len(paths)} standalone SVG diagrams.')


if __name__ == '__main__':
    main()
