# daniel90mm.github.io

Repository for [daniel90mm.github.io](https://daniel90mm.github.io/) and
adjacent projects that publish into it.

## Layout

- `museum/` -- Hugo site deployed to GitHub Pages.
- `museum/themes/PaperMod/` -- PaperMod theme submodule.
- `flightrecorder/` -- self-hosted brainstorming app under active development.
- `scripts/` -- repository-level helper scripts.

After cloning, initialize the theme submodule:

```sh
git submodule update --init --recursive
```

## Build

```sh
cd museum && hugo --gc --minify
```

## Preview

```sh
cd museum && hugo server --disableFastRender
```

## Deploy

Pushes to `main` trigger `.github/workflows/hugo.yml` which builds and publishes to
`https://daniel90mm.github.io/`.

Do not commit `museum/public/` -- it is generated.

## Repository Hygiene

After each meaningful change, run the relevant checks, commit the scoped files,
and push the branch. Do not include unrelated local edits, generated output, or
runtime secrets in the commit.

## Flightrecorder

Flightrecorder has its own entry point at
[flightrecorder/README.md](flightrecorder/README.md). Its quick verification
loop is:

```sh
cd flightrecorder
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

For targeted smoke checks, see
[flightrecorder/docs/SMOKE_COMMANDS.md](flightrecorder/docs/SMOKE_COMMANDS.md).
