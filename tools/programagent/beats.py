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
def card(folder, *files): return [folder] + [' ' + f for f in files]

ANA = 'a:analysis'; IMP = 'a:implement'; REVW = 'a:review'
REGIONS = ['a:ground', 'a:handoff', 'a:handoff-t', 'a:ws', 'a:ws-t', 'a:rev', 'a:rev-t']
# resting labels for every revision, swapped as the walkthrough advances
def impl_card(n): return card('📂 implementation-%03d/' % n, '📄 delivery.md', '📄 build.json ✓')
def rev_card(n, last=False): return card('📂 rev-%03d/' % n, '📁 source/', '📟 compile.sh', '⚙ executable ✓', '@' + REV[n]['commit']) + ([' last-stable'] if last else [])
def review_card(n, fx): return card('📂 review-%03d/' % n, '📄 review.md', fx)
WS0 = ['📂 workspace/', ' 📑 main.go']
WS4 = ['📂 workspace/', ' 📑 main.go', ' 📑 width.go']
WS5 = ['📂 workspace/', ' 📑 main.go', ' 📑 width.go', ' 📑 width_test.go']
BUILD = ['📂 internal/mod', ' 📑 mod.go', ' 📑 go.mod']
COMPILE = ['📟 compile.sh', 'go build', '→ ./executable']
WS_ALL = ['a:ws', 'a:ws-t', 'a:ws-src', 'a:ws-build', 'a:ws-compile']
def snap(to, delay=0): return [{'ids': WS_ALL, 'to': to, 'delay': delay}]
EMPTY = ['']

G = json.load(open(os.path.join(HERE, 'build', 'cells.json')))
LY = 545 * G['S'] + G['OY']          # a lane just below the Handoff region, above the pen icons
def into(stage, pen, card):
    """input card -> down to the lane -> across to the stage's pen -> down into the stage"""
    c = TC(card)
    return leg([[c[0], LY], [C(pen)[0], LY], C(pen), C(stage)], [card, pen, stage], litAt=[[card], [], [pen], [stage]], **{'from': c})
def candidate(revcard):
    """the candidate binary of a revision joins the review (a second, green dot)"""
    return leg([C('a:ic-copy'), C(REVW)], ['a:ic-copy'], color='pass', **{'from': TC(revcard)})
WS_CARDS = ['a:ws-src', 'a:ws-build', 'a:ws-compile']
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
beat('Revision 1', 'The developer reads analysis.md and starts revision 1',
     'A fresh session in /workspace with analysis.md as its only spec, %s. The gold binary is gone, so it can probe nothing — it writes Go from the document alone.' % phs('implementation-001'),
     legs=[into(IMP, 'a:ic-pen-i', 'a:h-analysis')], light=['a:arrow-ai'], throb=[IMP], frame=[['a:h-analysis'], [IMP]])
beat('Revision 1', 'Source lands in the workspace',
     'main.go (flags, stdin decode, filters, table layout), internal/mod/mod.go (the Module / Update model), go.mod (stdlib only) and compile.sh (an offline go build). %d lines of Go.' % REV[1]['go_lines'],
     legs=[leg([C('a:ic-code'), TC('a:ws-src')], ['a:ic-code', 'a:ws', 'a:ws-t'])],
     produce=[{'ids': ['a:ws-src'], 'delay': 0}, {'ids': ['a:ws-build'], 'delay': 350}, {'ids': ['a:ws-compile'], 'delay': 700}],
     text={'a:ws-src': WS0, 'a:ws-build': BUILD, 'a:ws-compile': COMPILE}, frame=[[IMP], WS_CARDS])
beat('Revision 1', 'Independent build → rev-001',
     'Once the developer session has ended, the orchestrator archives the committed tree (@%s), runs compile.sh itself and records the sha256 in build.json. The candidate binary is immutable from here on.' % REV[1]['commit'],
     legs=[leg([C('a:ws-compile'), [C('a:ic-archive')[0], C('a:ws-compile')[1]], C('a:ic-archive'), P('a:arrow-store', 1), TC('a:rev-1')], ['a:rev', 'a:rev-t', 'a:ic-archive', 'a:arrow-store', 'a:rev-1'])],
     text={'a:rev-1': rev_card(1)}, snap=snap('a:rev-1'), produce=[{'ids': ['a:rev-1'], 'delay': 1250}], flag='pass',
     marks=[{'at': [BB('a:rev-1')[2] - 6, BB('a:rev-1')[1] + 6], 'kind': 'pass', 'delay': 1400}], metrics='r1')
beat('Revision 1', 'delivery.md goes into the handoff',
     'What was built, which files changed, the developer\'s own test results, known limitations. The orchestrator adds independent-build.json and seals implementation-001/ read-only.',
     legs=[leg([C(IMP), C('a:ic-pen-i'), TC('a:h-impl')], ['a:ic-pen-i'])], start=C(IMP),
     produce=[{'ids': ['a:h-impl'], 'delay': 0}], text={'a:h-impl': impl_card(1)}, throb=['a:h-impl'], frame=[[IMP], ['a:h-impl']])
beat('Revision 1', 'The reviewer takes delivery.md and the rev-001 binary',
     'A third role, %s. Its inputs are the handoff so far and the candidate built by the orchestrator — never the developer\'s working directory. It re-runs the §6 matrix on gold and candidate in fresh fixture directories: stdout bytes, first stderr line, exit status — every row matches.' % phs('review-001'),
     legs=[into(REVW, 'a:ic-pen-r', 'a:h-impl'), candidate('a:rev-1')], light=['a:ic-loop'], throb=[REVW], parallel=True,
     frame=[['a:h-impl'], ['a:rev-1'], [REVW]])
beat('Revision 1', 'review-001: three accepted findings',
     'Then it probes what the matrix never covered. F1 HIGH — Main:true modules must be dropped · F2 HIGH — Replace redirects Version/Time/Update · F3 MEDIUM — the Module/ModuleError structure for error-string parity. Each with a fixture and a generalized requirement for the next revision.',
     legs=[leg([C('a:ic-pen-r'), TC('a:h-rev')], ['a:ic-pen-r'])], start=C(REVW),
     produce=[{'ids': ['a:h-rev'], 'delay': 0}], text={'a:h-rev': review_card(1, '📄 fixtures ×3')}, flag='fail', throb=['a:h-rev'], frame=[[REVW], ['a:h-rev']],
     marks=[{'at': [BB('a:h-rev')[2] - 6, BB('a:h-rev')[1] + 6], 'kind': 'fail', 'onArrive': True}])
# ── Revisions 2–3 ──────────────────────────────────────────────────────
# One beat per phase. A developer beat runs review-00N -> Implement -> the
# workspace; a reviewer beat runs delivery.md + the candidate -> Review ->
# review.md. The handoff cards always show the latest folder of each kind;
# earlier ones collapse into the small tab above.
beat('Revisions 2–3', 'Revision 2: review-001 is the spec, the workspace is rewritten',
     '%s. The developer reads review-001 (F1–F3) on top of analysis.md and changes main.go and mod.go: +31 lines — Main-module drop up front, Replace redirection after the filters, a recursive *Module model. delivery.md goes to implementation-002/.' % phs('implementation-002'),
     legs=[into(IMP, 'a:ic-pen-i', 'a:h-rev')], light=['a:ic-loop'], throb=[IMP],
     text={'a:h-impl-tab': ['📁 implementation ×1'], 'a:h-impl': impl_card(2)},
     produce=[{'ids': ['a:ws-src', 'a:ws-build'], 'delay': 200}, {'ids': ['a:h-impl', 'a:h-impl-tab'], 'delay': 900}], frame=[['a:h-rev'], [IMP], WS_CARDS])
beat('Revisions 2–3', 'rev-002: the workspace is stored as a second revision',
     'The same independent build as before: the orchestrator archives the committed tree (@%s), runs compile.sh itself and records the sha256. The dotted lines mark the live workspace each card was taken from.' % REV[2]['commit'],
     at=C('a:ws-compile'), text={'a:rev-2': rev_card(2)}, snap=snap('a:rev-2', 200), produce=[{'ids': ['a:rev-2'], 'delay': 1450}], flag='pass',
     marks=[{'at': [BB('a:rev-2')[2] - 6, BB('a:rev-2')[1] + 6], 'kind': 'pass', 'delay': 1600}], metrics='r2', hold=4200)
beat('Revisions 2–3', 'Review 2: delivery.md + rev-002 → everything matches',
     '%s. It reruns the §6 matrix and the F1–F3 fixtures on gold and candidate: all match. review-002 says there is no new functional requirement beyond preserving this parity.' % phs('review-002'),
     legs=[into(REVW, 'a:ic-pen-r', 'a:h-impl'), candidate('a:rev-2')], light=['a:ic-loop'], throb=[REVW], parallel=True,
     text={'a:h-rev-tab': ['📁 review ×1'], 'a:h-rev': review_card(2, '📄 fixtures ×2')},
     produce=[{'ids': ['a:h-rev', 'a:h-rev-tab'], 'delay': 300}], flag='pass', frame=[['a:h-impl'], ['a:rev-2'], [REVW], ['a:h-rev']],
     marks=[{'at': [BB('a:h-rev')[2] - 6, BB('a:h-rev')[1] + 6], 'kind': 'pass', 'delay': 600}])
beat('Revisions 2–3', 'Revision 3: review-002 asks for nothing — same commit, a third build',
     '%s. No source change — the tree at @%s already satisfies every requirement, so the developer re-verifies an offline build and the regression matrix and hands off. rev-003 is byte-identical to rev-002.' % (phs('implementation-003'), REV[3]['commit']),
     legs=[into(IMP, 'a:ic-pen-i', 'a:h-rev')], light=['a:ic-loop'], frame=[['a:h-rev'], [IMP], WS_CARDS],
     text={'a:h-impl-tab': ['📁 implementation ×2'], 'a:h-impl': impl_card(3), 'a:rev-2': rev_card(3)},
     produce=[{'ids': ['a:h-impl', 'a:h-impl-tab'], 'delay': 0}, {'ids': ['a:rev-2'], 'delay': 1750}], snap=snap('a:rev-2', 500), metrics='r3')
# ── Revisions 4–5 ──────────────────────────────────────────────────────
beat('Revisions 4–5', 'Review 3: delivery.md + rev-003 → F4, Unicode display width',
     '%s. Byte len() against display width — CJK, fullwidth, emoji, combining marks. Every ASCII input still matches, so F4 is inert on realistic data but a real parity gap.' % phs('review-003'),
     legs=[into(REVW, 'a:ic-pen-r', 'a:h-impl'), candidate('a:rev-2')], light=['a:ic-loop'], throb=[REVW], parallel=True,
     text={'a:h-rev-tab': ['📁 review ×2'], 'a:h-rev': review_card(3, '📄 fixtures ×1')},
     produce=[{'ids': ['a:h-rev', 'a:h-rev-tab'], 'delay': 300}], flag='fail', frame=[['a:h-impl'], ['a:rev-2'], [REVW], ['a:h-rev']],
     marks=[{'at': [BB('a:h-rev')[2] - 6, BB('a:h-rev')[1] + 6], 'kind': 'fail', 'delay': 600}])
beat('Revisions 4–5', 'Revision 4: review-003 in hand, width.go is added → rev-004',
     'A hand-rolled display-width engine: contiguous wide ranges, per-rune sums. %s. %d lines of Go; the workspace is stored as rev-004.' % (phs('implementation-004'), REV[4]['go_lines']),
     legs=[into(IMP, 'a:ic-pen-i', 'a:h-rev'), leg([C('a:ic-code'), TC('a:ws-src')], ['a:ic-code', 'a:ws-src'], **{'from': C(IMP)})], light=['a:ic-loop'], throb=[IMP],
     text={'a:ws-src': WS4, 'a:h-impl-tab': ['📁 implementation ×3'], 'a:h-impl': impl_card(4), 'a:rev-2': rev_card(4)},
     snap=snap('a:rev-2', 700), produce=[{'ids': ['a:ws-src'], 'delay': 0}, {'ids': ['a:h-impl', 'a:h-impl-tab'], 'delay': 350}, {'ids': ['a:rev-2'], 'delay': 1950}],
     frame=[['a:h-rev'], [IMP], WS_CARDS], metrics='r4')
beat('Revisions 4–5', 'Review 4: delivery.md + rev-004 → F5 emoji clusters, F6 numeric alignment',
     'The longest phase, %s. ZWJ sequences collapse to one cluster, Regional-Indicator pairs, a sparse emoji table; numeric cells right-align. It ships 7 fixtures: .jsonl inputs with .gold outputs captured from the gold binary.' % phs('review-004'),
     legs=[into(REVW, 'a:ic-pen-r', 'a:h-impl'), candidate('a:rev-2')], light=['a:ic-loop'], throb=[REVW], parallel=True,
     text={'a:h-rev-tab': ['📁 review ×3'], 'a:h-rev': review_card(4, '📄 fixtures ×7')},
     produce=[{'ids': ['a:h-rev', 'a:h-rev-tab'], 'delay': 300}], flag='fail', frame=[['a:h-impl'], ['a:rev-2'], [REVW], ['a:h-rev']],
     marks=[{'at': [BB('a:h-rev')[2] - 6, BB('a:h-rev')[1] + 6], 'kind': 'fail', 'delay': 600}])
beat('Revisions 4–5', 'Revision 5: review-004 in hand, grapheme-aware width.go plus width_test.go → rev-005, the budget is spent',
     '%s. %d lines of Go. max_revisions = 5, so the workflow stops with status %s; last-stable = rev-005 @%s.' % (phs('implementation-005'), REV[5]['go_lines'], R['state']['status'], R['last_stable']['commit']),
     legs=[into(IMP, 'a:ic-pen-i', 'a:h-rev'), leg([C('a:ic-code'), TC('a:ws-src')], ['a:ic-code', 'a:ws-src'], **{'from': C(IMP)})], light=['a:ic-loop'], throb=[IMP],
     text={'a:ws-src': WS5, 'a:h-impl-tab': ['📁 implementation ×4'], 'a:h-impl': impl_card(5), 'a:rev-2': rev_card(5, True)},
     snap=snap('a:rev-2', 700), produce=[{'ids': ['a:ws-src'], 'delay': 0}, {'ids': ['a:h-impl', 'a:h-impl-tab'], 'delay': 350}, {'ids': ['a:rev-2'], 'delay': 1950}], flag='pass',
     frame=[['a:h-rev'], [IMP], WS_CARDS], marks=[{'at': [BB('a:rev-2')[2] - 6, BB('a:rev-2')[1] + 6], 'kind': 'pass', 'delay': 2100}], metrics='r5')
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
# every runtime label must fit its box (width and line count), like the resting labels do
from textw import measure
bad = []
for i, bt in enumerate(B):
    for k, lines in bt.get('text', {}).items():
        t = M(k).get('text')
        if not t or lines == EMPTY: continue
        if len(lines) > t['lines']: bad.append('beat %d %s: %d lines > %d' % (i + 1, k, len(lines), t['lines']))
        for ln in lines:
            w = measure(ln, t['fam'], t['bold'], t['fs'])
            if w > t['avail']: bad.append('beat %d %s: "%s" %.0f > %.0f' % (i + 1, k, ln, w, t['avail']))
assert not bad, '\n'.join(bad)
print('%d beats, %d examples, %d metric rows; missing ids: %s' % (len(B), len(EX), len(metrics['labels']), missing or 'none'))
for i, b in enumerate(B): print('%02d %-14s %s' % (i + 1, b['ph'], b['t']))
