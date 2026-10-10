# -*- coding: utf-8 -*-
"""Pull the real figures and snippets of one ProgramBench agent run into run.json.

Takes the run directory as its one argument. That path is internal and is
deliberately not written down here; run.json is committed so the page can be
rebuilt without it. Nothing from config.json (hosts, proxies, keys) is read.
"""
import json, os, re, glob, sys, collections, datetime as dt
if len(sys.argv) < 2:
    sys.exit('usage: harvest.py <run-directory>\n'
             'The run directory is internal and is not recorded here; run.json is\n'
             'committed so the page can be rebuilt without it.')
RUN = sys.argv[1]
A = os.path.join(RUN, 'agent'); W = os.path.join(A, 'workflow'); H = os.path.join(A, 'handoff'); V = os.path.join(RUN, 'verifier')
OUT = os.path.join(os.path.dirname(__file__), 'run.json')
rd = lambda *p: open(os.path.join(*p), encoding='utf-8').read()
def section(text, start, stops):
    out = []; on = False
    for ln in text.split('\n'):
        if ln.startswith(start): on = True
        elif on and any(ln.startswith(s) for s in stops): break
        if on: out.append(ln)
    return '\n'.join(out).rstrip()
def ts(s): return dt.datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S')

res = json.load(open(os.path.join(RUN, 'result.json')))
phases = json.load(open(os.path.join(W, 'phases.json')))
state = json.load(open(os.path.join(W, 'state.json')))
last = json.load(open(os.path.join(W, 'last-stable.json')))

# per-phase session stats: turns, tool calls, wall time
sess = {}
for f in glob.glob(os.path.join(W, 'sessions', '*', 'projects', '*', '*.jsonl')):
    ph = f.split(os.sep)[-4]; turns = 0; tools = collections.Counter(); first = lastt = None
    for line in open(f, encoding='utf-8'):
        try: o = json.loads(line)
        except ValueError: continue
        t = o.get('timestamp')
        if t: first = first or t; lastt = t
        if o.get('type') == 'assistant':
            turns += 1
            for c in (o.get('message', {}).get('content') or []):
                if isinstance(c, dict) and c.get('type') == 'tool_use': tools[c['name']] += 1
    sess[ph.replace('-attempt-01', '')] = dict(turns=turns, tools=sum(tools.values()), bash=tools['Bash'],
                                              minutes=round((ts(lastt) - ts(first)).total_seconds() / 60), start=first[11:16] + 'Z')

# per-revision source size and build identity
revs = []
for n in range(1, 6):
    src = os.path.join(W, 'builds', 'rev-%03d' % n, 'source')
    gofiles = sorted(os.path.relpath(p, src) for p in glob.glob(os.path.join(src, '**', '*.go'), recursive=True))
    lines = sum(len(open(os.path.join(src, p), encoding='utf-8').read().splitlines()) for p in gofiles)
    b = json.load(open(os.path.join(W, 'builds', 'rev-%03d' % n, 'build.json')))
    revs.append(dict(n=n, files=gofiles, go_lines=lines, commit=b['source_commit'][:7], sha256=b['sha256'][:12], built=b['success']))

# verifier
ev = json.load(open(os.path.join(V, 'programbench_eval.json')))
st = collections.Counter(t['status'] for t in ev['test_results'])
per = collections.OrderedDict()
for t in ev['test_results']: per.setdefault(t['branch'][:6], collections.Counter())[t['status']] += 1
compile_step = next(x for x in ev['log'] if x['step'] == 'compile')
failed = [t['name'].split('.')[-1] for t in ev['test_results'] if t['status'] not in ('passed', 'skipped')]
rew = json.load(open(os.path.join(V, 'reward.json')))

ana = rd(H, 'analysis-initial', 'analysis.md')
r1 = rd(W, 'reviews', 'review-001', 'review.md'); r3 = rd(W, 'reviews', 'review-003', 'review.md'); r4 = rd(W, 'reviews', 'review-004', 'review.md')
d2 = rd(W, 'revisions', 'rev-002.md'); d3 = rd(W, 'revisions', 'rev-003.md'); d5 = rd(W, 'revisions', 'rev-005.md')
help_block = re.search(r'```\n(Usage of \./executable:.*?)```', ana, re.S).group(1).rstrip()
table_block = re.search(r'```\n(\+-{10,}.*?)```', ana, re.S).group(1).rstrip()

run = {
    'task': {'repo': 'psampaz/go-mod-outdated', 'commit': 'bb79367', 'lang': 'Go',
             'what': 'reads the JSON-lines output of `go list -u -m -json all` on stdin and prints a table of outdated modules'},
    # shown on the page as ProgramAgent; the harness id (claude-code-multi-v3) is kept for provenance
    'agent': {'name': 'ProgramAgent', 'harness': res['agent_info']['name'], 'model': res['agent_info']['model_info']['name'], 'claude_code': res['agent_info']['version']},
    'tokens': {'in': res['agent_result']['n_input_tokens'], 'out': res['agent_result']['n_output_tokens']},
    'wall_minutes': round((ts(res['agent_execution']['finished_at']) - ts(res['agent_execution']['started_at'])).total_seconds() / 60),
    'phases': [dict(p, **sess.get(p['phase'].replace('-attempt-01', ''), {})) for p in phases],
    'state': state, 'last_stable': {'revision': last['revision'], 'commit': last['source_commit'][:7], 'status': last['status']},
    'revisions': revs,
    'findings': [
        {'id': 'F1', 'rev': 1, 'sev': 'HIGH', 't': '`Main: true` modules must be dropped'},
        {'id': 'F2', 'rev': 1, 'sev': 'HIGH', 't': '`Replace` redirects Version / Time / Update for display and `-ci`'},
        {'id': 'F3', 'rev': 1, 'sev': 'MEDIUM', 't': '`Module`/`ModuleError` structure must match gold for error-string parity'},
        {'id': 'F4', 'rev': 3, 'sev': 'MEDIUM-HIGH', 't': 'column width, padding and header centering by Unicode display width, not bytes'},
        {'id': 'F5', 'rev': 4, 'sev': 'MEDIUM-HIGH', 't': 'display-width engine incomplete: Emoji-ZWJ clusters, Regional-Indicator pairs, sparse emoji table'},
        {'id': 'F6', 'rev': 4, 'sev': 'MEDIUM', 't': 'per-cell numeric right-alignment'},
    ],
    'verifier': {'total': len(ev['test_results']), 'passed': st['passed'], 'failed': st['failure'], 'skipped': st['skipped'],
                 'branches': len(ev['test_branches']), 'per_branch': {k: dict(v) for k, v in per.items()},
                 'compile_s': round(compile_step['wall_time'], 1), 'reward': round(rew['reward'], 4),
                 'almost_resolved': rew['almost_resolved'] == 1.0, 'resolved': rew['resolved'] == 1.0, 'failed_names': failed},
    'snips': {
        'help': help_block,
        'example_in': rd(H, 'analysis-initial', 'samples', 'example.jsonl').strip(),
        'example_out': table_block,
        'analysis_flags': section(ana, 'Flags (`flag` package', ['Outputs:']),
        'analysis_exit': section(ana, 'Outputs:', ['## 4']),
        'f1': section(r1, '### F1', ['### F2']),
        'deliv2_f1': section(d2, '### F1', ['### F2']),
        'f4': '\n'.join(section(r3, '### F4', ['- **Impact']).split('\n')[:7]),
        'f5': '\n'.join(section(r4, '### F5', ['- **Impact']).split('\n')[:14]),
        'rev3_note': section(d3, 'Accordingly this revision', ['hand off cleanly']) + '\nhand off cleanly.',
        'review2': section(r2 := rd(W, 'reviews', 'review-002', 'review.md'), 'Re-ran the high-value', ['| Case']),
        'fixture_in': rd(W, 'reviews', 'review-004', 'fixtures', 'fixture-numeric-align.jsonl').strip(),
        'fixture_gold': rd(W, 'reviews', 'review-004', 'fixtures', 'fixture-numeric-align.default.gold').rstrip(),
        'compile_sh': rd(W, 'builds', 'rev-005', 'source', 'compile.sh').rstrip(),
        'go_mod': rd(W, 'builds', 'rev-005', 'source', 'go.mod').rstrip(),
        'main_go': '\n'.join(rd(W, 'builds', 'rev-001', 'source', 'main.go').split('\n')[18:30]),
        'mod_go': '\n'.join(rd(W, 'builds', 'rev-005', 'source', 'internal', 'mod', 'mod.go').split('\n')[13:31]),
        'width_go': '\n'.join(rd(W, 'builds', 'rev-005', 'source', 'width.go').split('\n')[7:35]),
        'width_test': rd(W, 'builds', 'rev-005', 'source', 'width_test.go').rstrip(),
        'build_json': json.dumps(json.load(open(os.path.join(W, 'builds', 'rev-001', 'build.json'))), indent=2),
        'last_stable': json.dumps(last, indent=2), 'state_json': json.dumps(state, indent=2),
        'phases_json': json.dumps([{k: p[k] for k in ('phase', 'role', 'status') if k in p} for p in phases], indent=1),
        'build_cmd': ('# orchestrator, after the developer session has ended (no agent process alive):\n'
                      'git -C /workspace archive --format=tar "$commit" | tar -C build-00N/source -xf -\n'
                      'cd build-00N/source && chmod 0755 compile.sh\n'
                      'env -u HTTP_PROXY -u HTTPS_PROXY … timeout 300 bash ./compile.sh\n'
                      'test -f executable && sha256sum executable > build.json   # candidate is immutable from here'),
        'seal_cmd': ('chown -R root:root /handoff/implementation-001\n'
                     'chmod -R a-w,a+rX /handoff/implementation-001   # later agents read it, none can change it'),
        'verifier_sum': '\n'.join('%s  %s' % (k, '  '.join('%s %d' % (s, n) for s, n in v.items())) for k, v in per.items()),
    },
}
json.dump(run, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('run.json: %d phases, %d revisions, verifier %d/%d, %.0f KB' % (len(run['phases']), len(revs), st['passed'], len(ev['test_results']), os.path.getsize(OUT) / 1024))
for p in run['phases']: print('  %-24s turns %3d tools %2d  %2d min  start %s' % (p['phase'].replace('-attempt-01', ''), p.get('turns', 0), p.get('tools', 0), p.get('minutes', 0), p.get('start')))
