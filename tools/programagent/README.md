# Program agent walkthrough

`program-agent.html` is generated here, the way the Figure 2 walkthrough was
built: the drawio figure becomes an SVG whose every cell can be lit, framed or
relabelled, and a beat list replays one real ProgramBench run over it.

```
programagent.drawio      the figure (repo root)
run.json                 figures and snippets of the example run (committed; see harvest.py)
drawio2svg.py            figure -> build/fig.svgfrag + build/cells.json (text laid out with Liberation metrics)
beats.py                 cells + run.json -> build/beats.json, build/examples.json
head.html, body.html     page template: styles, markup, the playback engine
build.py                 assembles ../../program-agent.html
harvest.py               internal only: pulls run.json out of a harbor trial directory
```

Rebuild after editing any of these (then `python3 tools/gen.py` for the iframe cache-buster):

```sh
python3 tools/programagent/drawio2svg.py && python3 tools/programagent/beats.py && python3 tools/programagent/build.py
python3 tools/gen.py
```

`node tools/programagent/check.js` drives the engine headlessly through every
beat (a small DOM shim, no browser); run it after touching body.html.

The example run is the ProgramGym agent (harness claude-code-multi-v3, model deepseek-v4-flash) on
psampaz/go-mod-outdated: analysis → five implement/review revisions → verifier,
341 of 350 hidden tests. Labels in the figure follow that run beat by beat; the
figure's own generic labels (`***.cpp`, `Makefile`) are replaced in
`drawio2svg.py` (`TEXT`) and `beats.py`.
