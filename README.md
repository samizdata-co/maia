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

The skills in `template/…/.claude/skills/` are their only source; `copier.yml`'s `_exclude` decides which ones a project gets. To bring an existing project's skills up to date, run `gh skill install samizdata-co/maia <skill> --agent claude-code --force` in it once (this records the source), then `gh skill update --all`.

To add an outlet, create its brand repository (with `_brand.yml`, a Quarto extension and `datavis/mozaic/`), add it to the `outlet` choices in `copier.yml`, and vendor its files under conditional names (`{% if outlet == '<name>' %}…{% endif %}`) like the existing two.

## Spell checking

Every project includes `_extensions/maia/spellcheck`, a Lua filter that `_quarto.yml` runs on each render and preview. It pipes the prose of each document to Hunspell (which must be installed; without it the filter warns and the render carries on) and prints `file:line:column` warnings with suggestions. It checks in the project's `lang` (`ro` for Ziarul de Gardă, `en-GB` otherwise), switching for `[…]{lang=…}` spans and divs. The dictionaries are vendored from [LibreOffice/dictionaries](https://github.com/LibreOffice/dictionaries): Marco Pinto's en_GB (-ise) and rospell's ro_RO 3.3.10, with their licences next to them. Projects accept extra words through `WORDLIST`. To update a dictionary, copy the new `.aff` and `.dic` over the ones in `template/_extensions/maia/spellcheck/dictionaries/` and run the tests (`test_spellcheck_warns_about_mistakes` renders a document when `quarto` and `hunspell` are installed).

## Charts

`charts: mozaic` adds a `charts/` folder with [mozaic](https://github.com/samizdata-co/mozaic) charts built as static embeds, a preview page and print export, plus Claude Code skills for building charts, for cover images (an FT-style collage of a photo and the story's data lines, `.claude/skills/cover-image`) and for social media images of the charts (`pnpm social`: PNGs of the story's charts at Instagram, story, Bluesky/X and link-post sizes in `output/social/`, `.claude/skills/social-images`). Its house style is the outlet's mozaic theme, copied from the brand's `datavis/mozaic/` folder into `charts/src/lib/brands/<outlet>/` (mozaic's neutral `base` for no outlet). `chart_locales` sets the chart languages (ZdG defaults to `ro`, the others to `en`). The charts install mozaic from npm (`@samizdata/mozaic`), at the version in `mozaic_version` in `copier.yml`. With `--trust`, Copier runs `pnpm install` in `charts/`.

To develop mozaic itself from a project, link a local checkout instead of npm (pass the same `--data` to `copier update`, or it switches back to npm):

``` bash
uvx copier copy --trust --data charts=mozaic --data mozaic_path=$HOME/Projects/mozaic gh:samizdata-co/maia my-project
```

and build the library once in the checkout (`pnpm --filter mozaic package`).

After each mozaic release, set `mozaic_version` to the new version and release the template; `test_mozaic_version_matches_mozaic` fails while they differ (with a sibling mozaic checkout).

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
├── docs                                # analysis of already cleaned data, and the article
│   ├── analysis.ext                    # Quarto, Jupyter or Observable notebook
│   └── story.md                        # article
├── output                              # publishable notebooks, dashboards, charts, stories, etc.
├── charts                              # (mozaic) charts: src/charts/, data/, preview and embeds
├── _extensions/<org>/<outlet>          # pinned Quarto brand of the outlet
├── _extensions/maia/spellcheck        # spell check on render, with en_GB and ro_RO dictionaries
├── WORDLIST                            # words the spell check accepts
├── fonts                               # (SAMIZDATA) offline PDF copies of brand fonts
├── _quarto.yml                         # Quarto config
├── .gitignore                          # files to be ignored by version control
├── .Rprofile                           # (R) environment variables
├── <project_slug>.Rproj               # (R) RStudio project
├── package.json                        # (Observable) run scripts
├── README.md                           # boilerplate with instructions, sources, etc
└── .copier-answers.yml                 # template answers, used by copier update
```
