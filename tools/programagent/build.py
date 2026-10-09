# -*- coding: utf-8 -*-
"""Assemble program-agent.html: head.html + body.html with the figure, the
beats and the hover examples inlined. Run the whole chain with:
    python3 tools/programagent/drawio2svg.py && python3 tools/programagent/beats.py && python3 tools/programagent/build.py
(harvest.py only when the example run changes; it needs the internal run directory.)"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
rd = lambda *p: open(os.path.join(HERE, *p), encoding='utf-8').read()
R = json.load(open(os.path.join(HERE, 'run.json'), encoding='utf-8'))
cells = json.load(open(os.path.join(HERE, 'build', 'cells.json')))
head = rd('head.html'); body = rd('body.html')
svg = rd('build', 'fig.svgfrag')
beats = json.load(open(os.path.join(HERE, 'build', 'beats.json'), encoding='utf-8'))
body = (body.replace('__SVG__', svg)
            .replace('__VW__', '%g' % cells['VW']).replace('__VH__', '%g' % cells['VH'])
            .replace('__DATA__', json.dumps(beats, ensure_ascii=False, separators=(',', ':')))
            .replace('__EX__', rd('build', 'examples.json'))
            .replace('__REPO__', R['task']['repo']).replace('__COMMIT__', R['task']['commit']).replace('__LANG__', R['task']['lang'])
            .replace('__AGENT__', R['agent']['name']).replace('__MODEL__', R['agent']['model'])
            .replace('__NREV__', str(R['state']['completed_revisions'])).replace('__MAXREV__', str(R['state']['max_revisions']))
            .replace('__PASSED__', str(R['verifier']['passed'])).replace('__TOTAL__', str(R['verifier']['total'])).replace('__REWARD__', '%.3f' % R['verifier']['reward'])
            .replace('01 / 17', '01 / %d' % len(beats['beats'])).replace('17 beats', '%d beats' % len(beats['beats'])))
assert '__' not in re.sub(r'__[a-z]', '', body.replace('__proto__', '')) or True
left = re.findall(r'__[A-Z]+__', body); assert not left, left
page = '<!doctype html>\n<html lang="en" data-theme="light">\n<head>\n' + head + '\n</head>\n<body>\n' + body + '\n</body>\n</html>\n'
out = os.path.join(ROOT, 'program-agent.html')
open(out, 'w', encoding='utf-8').write(page)
js = body[body.index('<script>') + 8:body.rindex('</script>')]
open(os.path.join(HERE, 'build', 'page.js'), 'w', encoding='utf-8').write(js)
print('program-agent.html: %.0f KB, %d beats' % (len(page) / 1024, len(beats['beats'])))
