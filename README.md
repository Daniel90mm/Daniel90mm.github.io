# daniel90mm.github.io

- `museum/` -- Hugo site deployed to GitHub Pages at [daniel90mm.github.io](https://daniel90mm.github.io/).
- `flightrecorder/` -- brainstorming web app under active development.

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
