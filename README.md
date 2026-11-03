A [Copier](https://copier.readthedocs.io/en/stable/) template for data journalism projects. Named after the Romanian word for sourdough starter.

## Creating a project

Run the following command, replacing `my-project` with the folder to create. The folder name is used as the default project slug.

``` bash
uvx copier copy --trust gh:samizdata-co/maia my-project
```

`--trust` lets the template run its setup tasks (`npm install` for Observable, `uv venv` for uv projects). Without it, Copier refuses to generate the project. To skip the flag, add the template to `trust` in [Copier's settings file](https://copier.readthedocs.io/en/stable/settings/).

## Updating a project

Each project records its answers and template version in `.copier-answers.yml`. To pull template changes (for example a new brand release) into an existing project, commit your work and run the following command from the project folder.

``` bash
uvx copier update --trust
```

Copier merges template changes with your own edits and marks any conflicts in the affected files. Updates follow the template's Git tags, so tag a release (e.g. `v1.1.0`) after changing the template.

## Testing

Template checks can be run with `uv run -m unittest discover -s tests -v`.

## Outlets

The `outlet` question picks the brand for reports and charts: **SAMIZDATA** (the default), **Ziarul de Gardă** or **None**. Each outlet's brand lives in its own repository, and the template vendors a pinned copy, so generated projects never fetch a mutable remote dependency:

| Outlet          | Brand repository                                                       | Quarto extension                         | PDF                                                                 |
| --------------- | ---------------------------------------------------------------------- | ---------------------------------------- | ------------------------------------------------------------------- |
| SAMIZDATA       | [`samizdata-co/brand`](https://github.com/samizdata-co/brand)          | `_extensions/samizdata-co/samizdata`     | vendored Space Grotesk and Work Sans, `samizdata-pdf.tex` and `samizdata-before-body.tex` |
| Ziarul de Gardă | [`ziaruldegarda/brand`](https://github.com/ziaruldegarda/brand)        | `_extensions/ziaruldegarda/zdg`          | `zdg-pdf.tex`; Source Serif Pro and Source Sans Pro when installed  |
| None            |                                                                        |                                          |                                                                     |

The SAMIZDATA extension is pinned at [`samizdata-co/brand@v0.1.0`](https://github.com/samizdata-co/brand/tree/v0.1.0). Update an extension deliberately by running `quarto update extension samizdata-co/brand@<tag>` (or `ziaruldegarda/brand@<tag>`) inside `template/` and moving the result into the outlet's conditional folder, then regenerate and test a project before committing.

To add an outlet, create its brand repository (with `_brand.yml`, a Quarto extension and `datavis/mozaic/`), add it to the `outlet` choices in `copier.yml`, and vendor its files under conditional names (`{% if outlet == '<name>' %}…{% endif %}`) like the existing two.

## Charts

`charts: mozaic` adds a `charts/` folder with [mozaic](https://github.com/nicucalcea/mozaic) charts built as static embeds, a preview page and print export, plus a Claude Code skill for building charts. Its house style is the outlet's mozaic theme, copied from the brand's `datavis/mozaic/` folder into `charts/src/lib/brands/<outlet>/` (mozaic's neutral `base` for no outlet). `chart_locales` sets the chart languages (ZdG defaults to `ro,ru`, the others to `en`) and `mozaic_path` the mozaic checkout that `charts/package.json` links (default `../mozaic`). With `--trust`, Copier runs `pnpm install` in `charts/`.

When a brand releases a new mozaic theme, copy its `datavis/mozaic/*.ts` over the template's copy; the tests check that the copies match sibling checkouts of the brand repositories.

## Structure

Here's the current folder structure.

```         
.
├── data
│   ├── handmade                        # data created by hand
│   ├── interim                         # various bits and pieces, i.e. for transfer between tools
│   ├── processed                       # final datasets
│   └── raw                             # raw, immutable data
├── etl                                 # scripts to clean and process data
├── notebooks                           # analysis of already cleaned data
│   └── analysis.ext                    # Quarto, Jupyter or Observable notebook
├── output                              # publishable notebooks, dashboards, charts, stories, etc.
├── charts                              # (mozaic) charts: src/charts/, data/, preview and embeds
├── _extensions/<org>/<outlet>          # pinned Quarto brand of the outlet
├── fonts                               # (SAMIZDATA) offline PDF copies of brand fonts
├── _quarto.yml                         # Quarto config
├── .gitignore                          # files to be ignored by version control
├── .Rprofile                           # (R) environment variables
├── <project_slug>.Rproj               # (R) RStudio project
├── package.json                        # (Observable) run scripts
├── README.md                           # boilerplate with instructions, sources, etc
├── .copier-answers.yml                 # template answers, used by copier update
└── story.md                            # article
```
