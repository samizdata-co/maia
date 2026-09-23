# {{ cookiecutter.project_name }}

{{ cookiecutter.project_short_description }}

## Setup instructions

{% if cookiecutter.notebook == 'Quarto' %}To render the Quarto notebook, run `quarto render` on your `.qmd` file in `notebooks`.
{% elif cookiecutter.notebook == 'Jupyter' %}To render the Jupyter Notebooks using Quarto, run `quarto render` on your `.ipynb` file in `notebooks`.
{% elif cookiecutter.notebook == 'Observable' %}To build the Observable Notebook run `npm run dev` to preview or `npm run build` to build it to the `output` directory.
{% endif %}

{% if cookiecutter.interactive == 'Svelte + Layer Cake' %}## Interactive graphics

The `visuals/` workspace builds story-specific Svelte custom elements with Layer Cake and the pinned `@samizdata/graphics` package. Its `pnpm-workspace.yaml` explicitly permits that Git dependency's `prepare` build.

```bash
cd visuals
pnpm install
pnpm dev
pnpm check
pnpm build
```

- Add browser-safe publication files to `data/processed/web/`, then explicitly list each relative path in `visuals/data-manifest.json`.
- `pnpm prepare:data` rejects escaping or missing paths, removes stale generated files, and copies only allowlisted files into `visuals/static/data/`; Vite then copies them into the portable output directory.
- Add story compositions under `visuals/src/graphics/`, experiments under `visuals/src/local/`, and outer custom-element wrappers under `visuals/src/elements/`. Register all story elements once in `visuals/src/register.ts`.
- The build writes a relative ES-module bundle, `embed.html`, and publication data to `output/interactives/{{ cookiecutter.project_slug }}/`. Serve that directory over HTTP; do not open the HTML through `file://`.
- The example accepts `data-url`, `locale`, or a `data` element property. Keep attribute APIs semantic and expose shadow parts deliberately.
- Commit `visuals/pnpm-lock.yaml`, source, the manifest, and publication-safe `data/processed/web/` inputs. `visuals/static/data/` is generated. Decide whether built `output/interactives/` is committed according to the publication repository's deployment policy; never edit generated copies manually.
- Never allowlist confidential or non-public processed data. Do not change the pinned graphics tag without reviewing and rebuilding the story.

{% endif %}## SAMIZDATA report styling

- This project includes the pinned SAMIZDATA Quarto Brand Extension under `_extensions/`.
- PDF reports use the same Space Grotesk and Work Sans families from vendored files in `fonts/`.
- `samizdata-pdf.tex` and `samizdata-before-body.tex` contain only PDF delivery and composition overrides.

## Tracking time

This project uses [klog](https://klog.jotaen.net/) to track time spent on it.

You can start tracking time by running:

```bash
klog start hours.klg
```

To stop tracking time, run:

```bash
klog stop hours.klg
```

Or to take a break:

```bash
klog pause --summary 'Lunch break' hours.klg
```
