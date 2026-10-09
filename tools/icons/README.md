# Icon sources

`tools/gen.py` folds every `.svg` here into the inline `<symbol>` sprite in
`index.html`. Two kinds of file live here and `sprite()` tells them apart by
whether the file declares a `fill`:

| file | source | kind |
| --- | --- | --- |
| `claude` `deepseek` `docker` `github` `huggingface` `kimi` `openai` `qwen` `zai` | [simple-icons](https://github.com/simple-icons/simple-icons) | monochrome |
| `rust` | [devicon](https://github.com/devicons/devicon) `rust-original` | monochrome |
| `cplusplus` `go` `google` | devicon `*-original` | full colour |
| `c` | derived — see below | full colour |

**Monochrome** files carry no `fill`, so the shapes inherit `fill: currentColor`
and the `.i-*` tokens in `main.css` tint them per theme. That is what turns the
Rust gear white on a dark panel.

**Full colour** files are wrapped in `<g fill="#000">` at sprite time so the
shapes that rely on SVG's black default — the Go gopher's outlines — keep it
instead of inheriting `currentColor`.

## The C hexagon

Devicon ships only a flat grey letter for C (`c-original`), but Figure 1 of the
paper prints the blue hexagon that pairs with the C++ one. `c.svg` is devicon's
`cplusplus-original` with the two `+` glyphs removed from its white path: the
C is already a ring centred on the hexagon's own centre, so dropping them
leaves it centred. Regenerate it by re-running that edit, not by hand-drawing.
