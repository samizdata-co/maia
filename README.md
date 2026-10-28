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

## Quarto branding

Generated projects vendor the pinned SAMIZDATA Quarto Brand Extension from [`samizdata-co/brand@v0.1.0`](https://github.com/samizdata-co/brand/tree/v0.1.0). The extension is committed into each generated project, so rendering never fetches a mutable remote dependency.

Matching Space Grotesk and Work Sans files are included for offline PDF rendering, with PDF-only composition in `samizdata-pdf.tex` and `samizdata-before-body.tex`. Update the template's extension deliberately by running `quarto update extension samizdata-co/brand@<tag>` inside `template/`, and regenerate/test a project before committing.

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
├── _extensions/samizdata-co/samizdata # pinned SAMIZDATA Quarto brand
├── fonts                               # offline PDF copies of brand fonts
├── _quarto.yml                         # Quarto config
├── .gitignore                          # files to be ignored by version control
├── .Rprofile                           # (R) environment variables
├── <project_slug>.Rproj               # (R) RStudio project
├── package.json                        # (Observable) run scripts
├── README.md                           # boilerplate with instructions, sources, etc
├── .copier-answers.yml                 # template answers, used by copier update
└── story.md                            # article
```
