A [cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) template for data journalism projects. Named after the Romanian word for sourdough starter.

## Creating a project

Navigate to the directory where you want to create a new project and run the following command.

``` bash
uvx cookiecutter gh:nicucalcea/maia
```

## Optional interactive graphics

Choose `Svelte + Layer Cake` at the `interactive` prompt to generate a `visuals/` workspace. It pins an exact `@samizdata/graphics` version or Git tag, builds story-specific Svelte custom elements into one portable relative ES-module bundle, and copies only data explicitly allowlisted from `data/processed/web/`.

The default `None` choice preserves the existing generated project. The graphics package defaults to the immutable GitHub tag `github:samizdata-co/graphics#v0.0.1`; create that release before using the default in production, or enter another explicitly reviewed exact Git tag.

Template checks can be run with `uv run -m unittest discover -s tests -v`. To also install, type-check and build the generated interactive workspace against a local graphics checkout, run:

```bash
SAMIZDATA_GRAPHICS_PACKAGE=file:/path/to/graphics MAIA_TEST_FULL_BUILD=1 \
  uv run -m unittest discover -s tests -v
```

## Quarto branding

Generated projects vendor the pinned SAMIZDATA Quarto Brand Extension from [`samizdata-co/brand@v0.1.0`](https://github.com/samizdata-co/brand/tree/v0.1.0). The extension is committed into each generated project, so rendering never fetches a mutable remote dependency.

Matching Space Grotesk and Work Sans files are included for offline PDF rendering, with PDF-only composition in `samizdata-pdf.tex` and `samizdata-before-body.tex`. Update the template's extension deliberately with `quarto update extension samizdata-co/brand@<tag>` and regenerate/test a project before committing.

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
├── visuals                             # optional Svelte + Layer Cake custom-element workspace
├── _extensions/samizdata-co/samizdata # pinned SAMIZDATA Quarto brand
├── fonts                               # offline PDF copies of brand fonts
├── _quarto.yml                         # Quarto config
├── .gitignore                          # files to be ignored by version control
├── .Rprofile                           # (R) environment variables
├── {{cookiecutter.project_slug}}.Rproj # (R) RStudio project
├── package.json                        # (Observable) run scripts
├── README.md                           # boilerplate with instructions, sources, etc
└── story.md                            # article
```
