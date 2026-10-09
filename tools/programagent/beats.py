# -*- coding: utf-8 -*-
"""The walkthrough: beats.json (what each beat lights, where the pulse travels,
which labels change), examples.json (hover snippets) and metrics (per-revision
figures), all from build/cells.json + run.json."""
import json, os
HERE = os.path.dirname(__file__)
cells = json.load(open(os.path.join(HERE, 'build', 'cells.json')))['meta']
R = json.load(open(os.path.join(HERE, 'run.json'), encoding='utf-8'))
S = R['snips']; V = R['verifier']; PH = {p['phase'].replace('-attempt-01', ''): p for p in R['phases']}
REV = {r['n']: r for r in R['revisions']}
def M(n): return cells[n[2:] if n.startswith('a:') else n]
def C(n): return M(n)['c']
def TC(n): return M(n).get('tc', M(n)['c'])
def BB(n): return M(n)['bb']
def P(n, i): return M(n)['pts'][i]
def above(n, dy=0): b = BB(n); return [(b[0] + b[2]) / 2, b[1] + dy]
def below(n, dy=0): b = BB(n); return [(b[0] + b[2]) / 2, b[3] + dy]
def left(n, dx=0): b = BB(n); return [b[0] + dx, (b[1] + b[3]) / 2]
def right(n, dx=0): b = BB(n); return [b[2] + dx, (b[1] + b[3]) / 2]
def leg(pts, ids, **k): d = {'pts': pts, 'ids': ids}; d.update(k); return d
def ph(name, tu, to, mi): return '%d turns · %d tool calls · %d min' % (tu, to, mi)
def phs(k): p = PH[k]; return ph(k, p['turns'], p['tools'], p['minutes'])
def card(folder, *files): return [folder] + ['  ' + f for f in files]

ANA = 'a:analysis'; IMP = 'a:implement'; REVW = 'a:review'
REGIONS = ['a:ground', 'a:handoff', 'a:handoff-t', 'a:ws', 'a:ws-t', 'a:rev', 'a:rev-t']
# resting labels for every revision, swapped as the walkthrough advances
def impl_card(n): return card('📂 implementation-%03d/' % n, '📄 delivery.md', '📄 build.json ✓')
def rev_card(n, last=False): return card('📂 rev-%03d/' % n, '📁 source/ @' + REV[n]['commit'], '📟 compile.sh', '⚙ executable ✓') + (['  last-stable'] if last else [])
def review_card(n, fx): return card('📂 review-%03d/' % n, '📄 review.md', fx)
WS0 = ['📂 workspace/', '  📑 main.go', '  📑 go.mod']
WS4 = ['📂 workspace/', '  📑 main.go', '  📑 width.go', '  📑 go.mod']
WS5 = ['📂 workspace/', '  📑 main.go', '  📑 width.go', '  📑 width_test.go']
BUILD = ['📂 internal/mod', '  📑 mod.go', '  ···']
COMPILE = ['📟 compile.sh', 'go build', '→ ./executable']
WS_ALL = ['a:ws', 'a:ws-t', 'a:ws-src', 'a:ws-build', 'a:ws-compile']
def snap(to, delay=0): return [{'ids': WS_ALL, 'to': to, 'delay': delay}]
EMPTY = ['']

B = []
def beat(phase, t, d, **k): b = {'ph': phase, 't': t, 'd': d, 'legs': []}; b.update(k); B.append(b); return b

# ── Inputs ─────────────────────────────────────────────────────────────
beat('Inputs', 'The task: a black-box program and its docs',
     '%s @%s: a %s CLI that %s. The agent gets README.md, LICENSE and the gold ./executable (2.3 MB, execute-only) — no source.' % (R['task']['repo'], R['task']['commit'], R['task']['lang'], R['task']['what']),
     at=C('a:ic-docs'), light=['a:ic-docs', 'a:docs-t', 'a:ic-prog', 'a:prog-t'] + REGIONS, throb=['a:ic-docs', 'a:ic-prog'],
     frame=[['a:ic-docs', 'a:docs-t', 'a:ic-prog', 'a:prog-t']],
     text={'a:h-analysis': EMPTY, 'a:h-impl-tab': EMPTY, 'a:h-impl': EMPTY, 'a:h-rev-tab': EMPTY, 'a:h-rev': EMPTY,
           'a:ws-src': EMPTY, 'a:ws-build': EMPTY, 'a:ws-compile': EMPTY, 'a:rev-1': EMPTY, 'a:rev-2': EMPTY},
     fade=['a:h-analysis', 'a:h-impl-tab', 'a:h-impl', 'a:h-rev-tab', 'a:h-rev', 'a:ws-src', 'a:ws-build', 'a:ws-compile', 'a:rev-1', 'a:rev-2', 'a:link-top', 'a:link-bot'])
# ── Analysis ───────────────────────────────────────────────────────────
b = beat('Analysis', 'The analysis agent probes the executable',
     'A Claude Code session in a copy of the workspace, %s. It drives ./executable only through stdin and flags: -help, -update, -direct, -style markdown, -ci, malformed JSON, the nil-timestamp panic — and records bytes, stderr and exit codes.' % phs('analysis-initial'),
     start=C('a:ic-docs'), throb=[ANA], parallel=True, speed=1.2)
b['legs'] = [leg(P('a:docs-arrow', 1)[:1] + [P('a:docs-arrow', 2), C(ANA)], ['a:docs-arrow', ANA]),
             leg([P('a:prog-arrow', 1), P('a:prog-arrow', 2), C(ANA)], ['a:prog-arrow', ANA], **{'from': C('a:ic-prog')})]
b['legs'][0]['pts'] = [P('a:docs-arrow', 1), P('a:docs-arrow', 2), C(ANA)]
beat('Analysis', 'It writes analysis-initial/analysis.md',
     '17.9 KB: the interface inventory (4 flags, the stdin JSON-lines schema), exact stdout / stderr / exit evidence, requirements R1–R13 and a §6 regression matrix, plus samples/example.jsonl and dim.jsonl.',
     legs=[leg([C('a:ic-pen-a'), TC('a:h-analysis')], ['a:ic-pen-a'])],
     produce=[{'ids': ['a:h-analysis'], 'delay': 0}], text={'a:h-analysis': card('📂 analysis-initial/', '📄 analysis.md', '📄 samples/ ×2')}, throb=['a:h-analysis'])
beat('Analysis', 'The handoff is sealed read-only',
     'The orchestrator chowns analysis-initial/ to root and chmods it a-w; every later agent reads it, none can change it. The gold binary is removed from /handoff before a developer ever starts.',
     at=TC('a:h-analysis'), light=['a:handoff', 'a:handoff-t'], frame=[['a:handoff']], marks=[{'at': right('a:h-analysis', -8)[:1] + [BB('a:h-analysis')[1] + 6], 'kind': 'pass', 'delay': 300}], flag='pass', hold=3200)
# ── Revision 1 ─────────────────────────────────────────────────────────
beat('Revision 1', 'The developer writes the first baseline',
     'A fresh session in /workspace with analysis.md as its only spec, %s. It reads the handoff, probes nothing (the gold binary is gone) and writes Go.' % phs('implementation-001'),
     legs=[leg([C(ANA), C('a:arrow-ai'), C(IMP)], ['a:arrow-ai', IMP])], throb=[IMP])
beat('Revision 1', 'Source lands in the workspace',
     'main.go (flags, stdin decode, filters, table layout), internal/mod/mod.go (the Module / Update model), go.mod (stdlib only) and compile.sh (an offline go build). %d lines of Go.' % REV[1]['go_lines'],
     legs=[leg([C('a:ic-code'), TC('a:ws-src')], ['a:ic-code', 'a:ws', 'a:ws-t'])],
     produce=[{'ids': ['a:ws-src'], 'delay': 0}, {'ids': ['a:ws-build'], 'delay': 350}, {'ids': ['a:ws-compile'], 'delay': 700}],
     text={'a:ws-src': WS0, 'a:ws-build': BUILD, 'a:ws-compile': COMPILE}, frame=[['a:ws-src', 'a:ws-build', 'a:ws-compile']])
beat('Revision 1', 'Independent build → rev-001',
     'Once the developer session has ended, the orchestrator archives the committed tree (@%s), runs compile.sh itself and records the sha256 in build.json. The candidate binary is immutable from here on.' % REV[1]['commit'],
     legs=[leg([C('a:ws-compile'), [C('a:ic-archive')[0], C('a:ws-compile')[1]], C('a:ic-archive'), P('a:arrow-store', 1), TC('a:rev-1')], ['a:rev', 'a:rev-t', 'a:ic-archive', 'a:arrow-store', 'a:rev-1'])],
     text={'a:rev-1': rev_card(1)}, snap=snap('a:rev-1'), produce=[{'ids': ['a:rev-1'], 'delay': 1250}], flag='pass',
     marks=[{'at': [BB('a:rev-1')[2] - 6, BB('a:rev-1')[1] + 6], 'kind': 'pass', 'delay': 1400}], metrics='r1')
beat('Revision 1', 'delivery.md goes into the handoff',
     'What was built, which files changed, the developer\'s own test results, known limitations. The orchestrator adds independent-build.json and seals implementation-001/ read-only.',
     legs=[leg([C(IMP), C('a:ic-pen-i'), TC('a:h-impl')], ['a:ic-pen-i'])],
     produce=[{'ids': ['a:h-impl'], 'delay': 0}], text={'a:h-impl': impl_card(1)}, throb=['a:h-impl'])
beat('Revision 1', 'The reviewer runs gold against candidate',
     'A third role, %s. It re-runs the §6 matrix on both binaries in fresh fixture directories, comparing stdout bytes, the first stderr line and the exit status: every row matches. Then it probes what the matrix never covered.' % phs('review-001'),
     legs=[leg([C(IMP), C('a:ic-loop'), C(REVW)], ['a:ic-loop', REVW])], throb=[REVW])
beat('Revision 1', 'review-001: three accepted findings',
     'F1 HIGH — Main:true modules must be dropped · F2 HIGH — Replace redirects Version/Time/Update · F3 MEDIUM — the Module/ModuleError structure for error-string parity. Each with a fixture and a generalized requirement for the next revision.',
     legs=[leg([C('a:ic-pen-r'), TC('a:h-rev')], ['a:ic-pen-r'])],
     produce=[{'ids': ['a:h-rev'], 'delay': 0}], text={'a:h-rev': review_card(1, '📄 fixture-*.jsonl ×3')}, flag='fail', throb=['a:h-rev'],
     marks=[{'at': [BB('a:h-rev')[2] - 6, BB('a:h-rev')[1] + 6], 'kind': 'fail', 'onArrive': True}])
# ── Revisions 2–3 ──────────────────────────────────────────────────────
beat('Revisions 2–3', 'Loop: revision 2 implements F1–F3',
     'The reviewer\'s handoff becomes the developer\'s spec, %s. +31 lines across main.go and mod.go: Main-module drop up front, Replace redirection after the filters, a recursive *Module model. rev-002 builds independently.' % phs('implementation-002'),
     legs=[leg([C(REVW), C('a:ic-loop'), C(IMP)], ['a:ic-loop', IMP]), leg([TC('a:ws-src')], ['a:ws-src'], **{'from': C(IMP)})],
     text={'a:h-impl-tab': ['📁 implementation-001'], 'a:h-impl': impl_card(2), 'a:h-rev-tab': ['📁 review-001'], 'a:h-rev': EMPTY, 'a:rev-2': rev_card(2)},
     light=['a:h-impl-tab', 'a:h-rev-tab', 'a:ic-copy'], snap=snap('a:rev-2', 400), produce=[{'ids': ['a:rev-2'], 'delay': 1650}], parallel=True, metrics='r2', speed=1.3)
beat('Revisions 2–3', 'Review 2 confirms; revision 3 changes nothing',
     'review-002 reruns everything: all match, no new defects. implementation-003 therefore re-verifies and re-delivers the same tree (rev-003 is the same commit @%s). %s.' % (REV[3]['commit'], phs('implementation-003')),
     legs=[leg([C(IMP), C('a:ic-loop'), C(REVW)], [REVW])],
     text={'a:h-rev': review_card(2, '📄 fixture-*.jsonl ×2'), 'a:h-impl-tab': ['📁 implementation-001…2'], 'a:h-impl': impl_card(3), 'a:rev-2': rev_card(3)},
     flag='pass', marks=[{'at': [BB(REVW)[2] - 4, BB(REVW)[1] + 4], 'kind': 'pass', 'onArrive': True}], metrics='r3', throb=['a:h-rev'],
     snap=snap('a:rev-2', 600), produce=[{'ids': ['a:rev-2'], 'delay': 1850}])
# ── Revisions 4–5 ──────────────────────────────────────────────────────
beat('Revisions 4–5', 'Review 3 finds F4: Unicode display width',
     'Byte len() against display width — CJK, fullwidth, emoji, combining marks. Every ASCII input still matches, so F4 is inert on realistic data but a real parity gap. %s.' % phs('review-003'),
     at=C(REVW), throb=[REVW, 'a:h-rev'], text={'a:h-rev-tab': ['📁 review-001…2'], 'a:h-rev': review_card(3, '📄 fixture-unicode.jsonl')},
     flag='fail', marks=[{'at': [BB('a:h-rev')[2] - 6, BB('a:h-rev')[1] + 6], 'kind': 'fail', 'delay': 400}])
beat('Revisions 4–5', 'Revision 4 adds width.go',
     'A hand-rolled display-width engine: contiguous wide ranges, per-rune sums. %s. %d lines of Go; rev-004 builds.' % (phs('implementation-004'), REV[4]['go_lines']),
     legs=[leg([C(REVW), C('a:ic-loop'), C(IMP), C('a:ic-code'), TC('a:ws-src')], [IMP, 'a:ic-code', 'a:ws-src'])],
     text={'a:ws-src': WS4, 'a:h-impl-tab': ['📁 implementation-001…3'], 'a:h-impl': impl_card(4), 'a:rev-2': rev_card(4)},
     snap=snap('a:rev-2', 700), produce=[{'ids': ['a:ws-src'], 'delay': 0}, {'ids': ['a:rev-2'], 'delay': 1950}], metrics='r4')
beat('Revisions 4–5', 'Review 4: F5 emoji clusters, F6 numeric alignment',
     'The longest phase, %s. ZWJ sequences collapse to one cluster, Regional-Indicator pairs, a sparse emoji table; numeric cells right-align. It ships 7 fixtures: .jsonl inputs with .gold outputs captured from the gold binary.' % phs('review-004'),
     legs=[leg([C(IMP), C('a:ic-loop'), C(REVW), C('a:ic-pen-r'), TC('a:h-rev')], [REVW, 'a:ic-pen-r', 'a:h-rev'])],
     text={'a:h-rev-tab': ['📁 review-001…3'], 'a:h-rev': review_card(4, '📄 fixtures ×7')}, produce=[{'ids': ['a:h-rev'], 'delay': 0}],
     flag='fail', marks=[{'at': [BB('a:h-rev')[2] - 6, BB('a:h-rev')[1] + 6], 'kind': 'fail', 'onArrive': True}])
beat('Revisions 4–5', 'Revision 5: grapheme-aware width.go, plus width_test.go — the budget is spent',
     '%s. %d lines of Go. max_revisions = 5, so the workflow stops with status %s; last-stable = rev-005 @%s.' % (phs('implementation-005'), REV[5]['go_lines'], R['state']['status'], R['last_stable']['commit']),
     legs=[leg([C(REVW), C('a:ic-loop'), C(IMP), C('a:ic-code'), TC('a:ws-src')], [IMP, 'a:ws-src'])],
     text={'a:ws-src': WS5, 'a:h-impl-tab': ['📁 implementation-001…4'], 'a:h-impl': impl_card(5), 'a:rev-2': rev_card(5, True)},
     snap=snap('a:rev-2', 700), produce=[{'ids': ['a:ws-src'], 'delay': 0}, {'ids': ['a:rev-2'], 'delay': 1950}], flag='pass',
     marks=[{'at': [BB('a:rev-2')[2] - 6, BB('a:rev-2')[1] + 6], 'kind': 'pass', 'delay': 2100}], metrics='r5')
# ── Verification ───────────────────────────────────────────────────────
beat('Verification', 'The verifier builds rev-005 and runs %d hidden test branches' % V['branches'],
     'compile.sh → ./executable in %.1f s, then %d test cases: %d passed, %d failed, %d skipped. The misses: one missing-timestamp crash case, and in a single branch the help text, the unknown-flag usage and the malformed-JSON exit code. Reward %.4f — almost resolved.' % (V['compile_s'], V['total'], V['passed'], V['failed'], V['skipped'], V['reward']),
     at=TC('a:rev-2'), throb=['a:rev-2'], frame=[['a:rev']], flag='pass', metrics='final', hold=6000,
     marks=[{'at': [BB('a:rev-2')[0] + 14 + 26 * i, BB('a:rev-2')[3] - 10], 'kind': ('fail' if i in (0, 3) else 'pass'), 'delay': 500 + 180 * i} for i in range(V['branches'])])

# ── metrics (per revision) ─────────────────────────────────────────────
def impl(n): return PH['implementation-%03d' % n]
def rev_(n): return PH['review-%03d' % n] if n < 5 else None
FOUND = {1: 0, 2: 3, 3: 3, 4: 4, 5: 6}   # findings implemented by that revision (cumulative)
OPEN = {1: 3, 2: 0, 3: 1, 4: 2, 5: 0}     # findings the review of that revision left open
metrics = {
    'labels': ['Go source lines', 'Findings implemented', 'Findings left open', 'Developer turns', 'Developer tool calls', 'Phase wall time'],
    'max': [600, 6, 3, 150, 40, 60], 'unit': ['', '/6', '', '', '', ' min'],
    'rows': {'r%d' % n: [REV[n]['go_lines'], FOUND[n], OPEN[n], impl(n)['turns'], impl(n)['tools'], impl(n)['minutes']] for n in range(1, 6)},
    'title': {'r%d' % n: 'Revision %d · build ✓ @%s' % (n, REV[n]['commit']) for n in range(1, 6)},
    'final': {'tests': '%d / %d' % (V['passed'], V['total']), 'reward': '%.4f' % V['reward'], 'wall': '%dh %02dm' % divmod(R['wall_minutes'], 60),
              'tokens': '%.1fM in · %dK out' % (R['tokens']['in'] / 1e6, R['tokens']['out'] / 1e3), 'branches': V['branches'], 'failed': V['failed'], 'skipped': V['skipped']},
}
# ── hover examples ─────────────────────────────────────────────────────
EX = [
    {'key': 'docs', 'ids': ['a:ic-docs', 'a:docs-t'], 'title': 'Docs — what the agent may read', 'src': 'README.md + LICENSE; the flag help as the analysis agent recorded it', 'blocks': [{'lang': './executable -help', 'code': S['help']}]},
    {'key': 'prog', 'ids': ['a:ic-prog', 'a:prog-t'], 'title': 'Program — the gold executable, as a black box', 'src': 'samples/example.jsonl → stdout, byte for byte (analysis.md §4)', 'blocks': [{'lang': 'stdin', 'code': S['example_in']}, {'lang': 'stdout', 'code': S['example_out']}]},
    {'key': 'analysis', 'ids': [ANA], 'title': 'Analysis — the interface inventory', 'src': 'analysis.md §3: flags, outputs and exit codes derived by probing only', 'blocks': [{'lang': 'flags', 'code': S['analysis_flags']}, {'lang': 'outputs · exit status', 'code': S['analysis_exit']}]},
    {'key': 'hanalysis', 'ids': ['a:h-analysis'], 'title': 'analysis-initial/ — sealed after the phase', 'src': 'the orchestrator makes every handoff directory read-only before the next role starts', 'blocks': [{'lang': 'orchestrator', 'code': S['seal_cmd']}, {'lang': 'phases.json', 'code': S['phases_json']}]},
    {'key': 'implement', 'ids': [IMP], 'title': 'Implement — the developer role', 'src': 'main.go as written in revision 1: the four flags, straight from analysis.md', 'blocks': [{'lang': 'main.go', 'code': S['main_go']}]},
    {'key': 'himpl', 'ids': ['a:h-impl', 'a:h-impl-tab'], 'title': 'delivery.md — revision 2, finding F1', 'src': 'the developer reports each accepted finding back in the same terms the reviewer used', 'blocks': [{'lang': 'delivery.md', 'code': S['deliv2_f1']}]},
    {'key': 'review', 'ids': [REVW], 'title': 'Review — gold vs candidate, differential', 'src': 'review-002 §2: how a regression pass is scored', 'blocks': [{'lang': 'review.md', 'code': S['review2']}]},
    {'key': 'hrev', 'ids': ['a:h-rev', 'a:h-rev-tab'], 'title': 'review-001 — finding F1', 'src': 'a finding is a reproducer, a generalized requirement and a fixture file', 'blocks': [{'lang': 'review.md', 'code': S['f1']}]},
    {'key': 'loop', 'ids': ['a:ic-loop'], 'title': 'The revision loop', 'src': 'review-003 → F4, review-004 → F5/F6: what each pass of the loop produced', 'blocks': [{'lang': 'review-003', 'code': S['f4']}, {'lang': 'review-004', 'code': S['f5']}]},
    {'key': 'fixture', 'ids': ['a:ic-pen-r'], 'title': 'A gold fixture from review-004', 'src': 'fixture-numeric-align.jsonl and the .gold output captured from the reference binary', 'blocks': [{'lang': 'stdin', 'code': S['fixture_in']}, {'lang': 'gold stdout', 'code': S['fixture_gold']}]},
    {'key': 'wssrc', 'ids': ['a:ws-src', 'a:ic-code'], 'title': 'width.go — revision 5', 'src': 'the grapheme-aware display-width function that closed F5', 'blocks': [{'lang': 'width.go', 'code': S['width_go']}]},
    {'key': 'wsbuild', 'ids': ['a:ws-build'], 'title': 'internal/mod/mod.go', 'src': 'the recursive data model that finding F3 asked for', 'blocks': [{'lang': 'mod.go', 'code': S['mod_go']}, {'lang': 'go.mod', 'code': S['go_mod']}]},
    {'key': 'compile', 'ids': ['a:ws-compile'], 'title': 'compile.sh', 'src': 'offline, stdlib only; the orchestrator and the verifier both run exactly this', 'blocks': [{'lang': 'compile.sh', 'code': S['compile_sh']}]},
    {'key': 'archive', 'ids': ['a:ic-archive', 'a:arrow-store'], 'title': 'Independent build', 'src': 'the orchestrator builds from the committed tree, never from the developer\'s working directory', 'blocks': [{'lang': 'orchestrator', 'code': S['build_cmd']}, {'lang': 'build.json', 'code': S['build_json']}]},
    {'key': 'rev1', 'ids': ['a:rev-1'], 'title': 'rev-001 — the first candidate', 'src': 'each revision keeps its own source snapshot and binary', 'blocks': [{'lang': 'build.json', 'code': S['build_json']}]},
    {'key': 'rev2', 'ids': ['a:rev-2', 'a:ic-copy', 'a:link-top', 'a:link-bot'], 'title': 'last-stable — what gets verified', 'src': 'the final state of the workflow after five revisions', 'blocks': [{'lang': 'last-stable.json', 'code': S['last_stable']}, {'lang': 'state.json', 'code': S['state_json']}, {'lang': 'verifier · per branch', 'code': S['verifier_sum']}]},
    {'key': 'wtest', 'ids': ['a:ic-pen-i'], 'title': 'width_test.go — the developer\'s own test', 'src': 'revision 5 ships its unit test alongside the fix', 'blocks': [{'lang': 'width_test.go', 'code': S['width_test']}]},
    {'key': 'rev3', 'ids': ['a:ic-pen-a'], 'title': 'delivery.md — revision 3', 'src': 'a revision may legitimately change nothing', 'blocks': [{'lang': 'rev-003.md', 'code': S['rev3_note']}]},
]
json.dump({'beats': B, 'metrics': metrics}, open(os.path.join(HERE, 'build', 'beats.json'), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(EX, open(os.path.join(HERE, 'build', 'examples.json'), 'w', encoding='utf-8'), ensure_ascii=False)
ids = set()
for b in B:
    for l in b['legs']: ids.update(l['ids'])
    for k in ('light', 'throb', 'fade'): ids.update(b.get(k, []))
    for pr in b.get('produce', []): ids.update(pr['ids'])
    ids.update(b.get('text', {}).keys())
missing = sorted(i for i in ids if i[2:] not in cells)
print('%d beats, %d examples, %d metric rows; missing ids: %s' % (len(B), len(EX), len(metrics['labels']), missing or 'none'))
for i, b in enumerate(B): print('%02d %-14s %s' % (i + 1, b['ph'], b['t']))
