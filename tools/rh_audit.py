#!/usr/bin/env python3
"""Small, read-only, source-level audit of a pinned Riemann Hypothesis Lean mirror.

This DOES NOT check proofs, resolve elaborated Lean terms, calculate transitive
kernel dependencies, or establish mathematical correctness. It finds selected
named declarations, checks the presence of expected source-level references,
and generates review artifacts for human auditors.
"""
import argparse
import json
import re
import subprocess
from datetime import date
from pathlib import Path

MIRROR = 'https://github.com/Deicyde/riemann-hypothesis'
PIN = 'e50d09817ad81469f737e8f637561e6ccf86c670'

DECLS = [
    dict(id='row', name='UpperTheory.Gal.Int.galoisLocalGlobalStrong_recParameter', file='src/Development/AutomorphicArithmetic/Foundations/GaloisRepresentations/IntegralStructures/RowSrc.lean', refs=['galoisRepresentations_of_thetaLift']),
    dict(id='vwin', name='UpperTheory.One.vwin_of_row', file='src/Development/AutomorphicArithmetic/AutomorphicVarieties/ModularityArgument/ThresholdArguments/DenseThresholdCases/VwinOfRow.lean', refs=['automorphic_window_of_inputs']),
    dict(id='literature', name='UpperTheory.LiteratureTheorems.every_character_of_literature_of_vWin', file='src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean', refs=['every_character_of_theta_integrals_local_matching']),
    dict(id='bridge', name='UpperTheory.FinalTheorems.everyCharacter_of_row', file='src/Development/AutomorphicArithmetic/CharacterBoxes/MainConclusion.lean', refs=['every_character_of_literature_of_vWin', 'vwin_of_row']),
    dict(id='every', name='UpperTheory.FinalTheorems.everyCharacter', file='src/Development/AutomorphicArithmetic/CharacterBoxes/MainConclusion.lean', refs=['everyCharacter_of_row', 'galoisLocalGlobalStrong_recParameter']),
    dict(id='predicate', name='UpperTheory.EveryCharacter', file='src/Development/AutomorphicArithmetic/CharacterBoxes/EveryCharacter.lean', refs=['DirichletCharacter.LFunction']),
    dict(id='allchi', name='allChi', file='src/Supplements/Kernels/MainTheorems.lean', refs=['UpperTheory.FinalTheorems.everyCharacter']),
    dict(id='rh_from_right', name='Formalism.VW.rh_of_right', file='src/Formalism/GammaFactorNonvanishing/RhOfRight.lean', refs=['riemannZeta_one_sub']),
    dict(id='rh_of_every', name='Formalism.VW.rh_of_every', file='src/Formalism/GammaFactorNonvanishing/CritLine.lean', refs=['Formalism.VW.rh_of_right', 'LFunction_modOne_eq']),
    dict(id='rh_of_all', name='rhOfAll', file='src/Supplements/Kernels/MainTheorems.lean', refs=['Formalism.VW.rh_of_every', 'allChi']),
    dict(id='headline', name='riemannHypothesis', file='src/Main.lean', refs=['rhOfAll']),
]
# Edges mean explicit use of or passage through a named source-level result.
# They are not a Lean elaborator-generated dependency graph.
EDGES = [
    ('row','every'), ('literature','bridge'), ('vwin','bridge'),
    ('bridge','every'), ('every','allchi'), ('allchi','rh_of_all'),
    ('rh_from_right','rh_of_every'), ('rh_of_every','rh_of_all'),
    ('rh_of_all','headline'),
]
# The predicate is a statement/type, so do not present it as a proof premise.
DECL_START = re.compile(r'^\s*(theorem|lemma|def|abbrev)\s+([\w\.\u0080-\uffff]+)(?=\s|\(|:|$)')
BOUNDARY = re.compile(r'^(?:theorem|lemma|def|abbrev|instance|structure|class|inductive|namespace|end)\b')


def git_head(root: Path) -> str | None:
    try:
        r = subprocess.run(['git','-C',str(root),'rev-parse','HEAD'], check=True, capture_output=True, text=True)
        return r.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def find_decl(source: str, qualified: str) -> dict:
    lines = source.splitlines()
    short = qualified.split('.')[-1]
    candidates = []
    for i, line in enumerate(lines):
        m = DECL_START.match(line)
        if not m:
            continue
        symbol = m.group(2)
        if symbol == qualified or symbol == short:
            candidates.append((i, symbol))
    if len(candidates) != 1:
        return {'found': False, 'reason': f'Expected one declaration; found {len(candidates)}'}
    i, symbol = candidates[0]
    j = i + 1
    while j < len(lines) and not BOUNDARY.match(lines[j]):
        j += 1
    return {'found': True, 'line': i + 1, 'declared_as': symbol,
            'block': '\n'.join(lines[i:j])}


def inspect(root: Path) -> list[dict]:
    out = []
    for spec in DECLS:
        fpath = root / spec['file']
        item = {k:v for k,v in spec.items() if k != 'refs'}
        item['url'] = f'{MIRROR}/blob/{PIN}/{spec["file"]}'
        item['expected_source_references'] = spec['refs']
        if not fpath.is_file():
            item.update(found=False, reason='Missing source file', refs_found={})
        else:
            found = find_decl(fpath.read_text(encoding='utf-8'), spec['name'])
            item['found'] = found['found']
            if found['found']:
                item['line'] = found['line']
                item['declared_as'] = found['declared_as']
                item['url'] += f'#L{found["line"]}'
                item['refs_found'] = {r:r in found['block'] for r in spec['refs']}
            else:
                item['reason'] = found['reason']
                item['refs_found'] = {}
        out.append(item)
    return out


def mermaid(items: list[dict]) -> str:
    ids = {x['id']:x for x in items}
    lines = ['flowchart TD']
    for x in items:
        name = x['name'].replace('"','\\"')
        lines.append(f'    {x["id"]}["{name}"]')
    for a,b in EDGES:
        lines.append(f'    {a} --> {b}')
    lines.append('    %% Source-level trace only. No Lean elaboration or kernel verification.')
    return '\n'.join(lines)+'\n'


def markdown_summary(items: list[dict], head: str | None) -> str:
    lines = ['# Static critical-path audit', '',
             f'- Expected mirror revision: `{PIN}`',
             f'- Local checkout revision: `{head or "not a Git checkout"}`',
             '- This checks selected source names and textual references only.', '',
             '| Declaration | Source location | Textual reference checks |',
             '|---|---|---|']
    for x in items:
        refs = x.get('refs_found',{})
        result = 'missing' if not x['found'] else f'{sum(refs.values())}/{len(refs)} observed'
        loc = f'[L{x["line"]}]({x["url"]})' if x.get('line') else 'missing'
        lines.append(f'| `{x["name"]}` | {loc} | {result} |')
    lines += ['', '**Important:** a matching reference string is neither a proof-term dependency'
              ' nor a check that a theorem is mathematically correct. Review the source and run'
              ' independent formal verification separately.', '']
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True, type=Path, help='Path to local clone of Deicyde/riemann-hypothesis')
    p.add_argument('--out', required=True, type=Path, help='Output directory (not inside proof clone)')
    p.add_argument('--allow-different-revision', action='store_true', help='Produce exploratory output for nonmatching revision; mark as unpinned')
    args = p.parse_args()
    root = args.root.resolve()
    out = args.out.resolve()
    head = git_head(root)
    if head != PIN and not args.allow_different_revision:
        p.error(f'Refusing unpinned checkout ({head!r}); expected {PIN}. Use --allow-different-revision only for exploratory work.')
    if out == root or root in out.parents:
        p.error('--out must be outside the proof source tree (read-only policy).')
    items = inspect(root)
    report = {'schema_version':1,'expected_commit':PIN,'actual_commit':head,
              'pinned':head==PIN,'method':'source-text scan only, NOT an elaborated Lean dependency or proof checker',
              'declarations':items,'source_edges':EDGES}
    out.mkdir(parents=True,exist_ok=True)
    (out/'audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (out/'critical-path.mmd').write_text(mermaid(items),encoding='utf-8')
    (out/'static-review.md').write_text(markdown_summary(items,head),encoding='utf-8')
    missing = [x['name'] for x in items if not x['found'] or not all(x['refs_found'].values())]
    print(f'Read-only audit: {len(items)} declarations; {len(missing)} missing references/declarations; pinned={head==PIN}')
    for name in missing:
        print('REVIEW:',name)
    if missing:
        raise SystemExit(2)

if __name__=='__main__':
    main()
