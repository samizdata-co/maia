---
name: release-template
description: How to ship changes to the maia Copier template — test, commit, push to main, pick a version, create the GitHub release and tag with gh, and check that Copier serves it. Use this whenever you change anything under template/ or copier.yml and the user wants it live, or asks to release, deploy, publish, ship, tag, bump the version, cut a release, update the brand extension, or make changes reach existing projects via `copier update` — even if they don't say "release".
---

# Releasing the maia template

maia is a [Copier](https://copier.readthedocs.io/) template hosted at **`samizdata-co/maia`** on GitHub (it used to be `nicucalcea/maia`; GitHub redirects the old name, but always use the new one). Generated projects record their answers and the template tag they came from in `.copier-answers.yml`, and `copier update` moves them to the newest tag. So a release is just a git tag: once it's pushed, every new and updated project gets it. Treat tags as public and permanent.

## Repo layout

- `copier.yml` — questions, validator, `_tasks`. `_subdirectory: template` means only `template/` is copied into projects.
- `template/` — the project skeleton.
  - Only files that use variables have the `.jinja` suffix; everything else (LaTeX, YAML, fonts) is copied verbatim, so `{%` in `.tex` files is safe. If you add a variable to a plain file, rename it to `*.jinja`.
  - Optional files use conditional names, e.g. `{% if notebook == 'Quarto' %}analysis.qmd{% endif %}.jinja`. A name that renders empty is skipped.
  - `{{ _copier_conf.answers_file }}.jinja` writes `.copier-answers.yml`. Don't remove it, or `copier update` stops working.
  - Dates use the `strftime` filter (`{{ '%Y' | strftime }}`), not `now()`, which Copier deprecated.
- `tests/test_generation.py` — generates projects with `uvx copier copy --vcs-ref HEAD`, so uncommitted changes are included (a `DirtyLocalWarning` is expected).
- Files outside `template/` and `copier.yml` (README, tests, this skill) never reach projects.

## Workflow

### 1. Test

```bash
uv run -m unittest discover -s tests -v
```

Add or adjust tests for whatever you changed. If a change touches `_tasks`, also do a real copy with tasks in a scratch directory (`uvx copier copy --trust --defaults --vcs-ref HEAD --data ... . <scratch>/test-project`). `_tasks` run on `copier update` too, so every task must be safe to repeat (that's why it's `uv venv --allow-existing`).

### 2. Decide whether this needs a release

Only changes to `template/` or `copier.yml` need a tag. README, test or skill changes only need commit and push.

Pick the version from the latest tag (`git tag --sort=-v:refname | head -1`):

- **Major** — breaks `copier update` for existing projects: a renamed or removed question, changed choice values, moved or renamed files. Add a `_migrations` entry to `copier.yml` where it helps, and say in the release notes what users must do.
- **Minor** — new files, new questions with defaults, brand extension bumps, new options.
- **Patch** — fixes to existing files.

Tags are `vX.Y.Z`. Copier picks the highest PEP 440 version, so never reuse, move or delete a tag. Projects pin the tag in `_commit`, and rewriting it breaks their updates.

### 3. Commit and push

The repo commits directly to `main` with short, lowercase subjects (e.g. `samizdata branding`, `slugify project slug`), and a body when the change needs explaining.

```bash
git fetch && git status -sb      # main must not be behind origin
git push origin main
```

Pushing and releasing are public. Do them when the user asked you to release or deploy; otherwise ask first.

### 4. Create the release and tag

`gh` creates the tag on GitHub as part of the release:

```bash
gh release create vX.Y.Z -R samizdata-co/maia --target main --title "vX.Y.Z: <summary>" --notes-file - <<'EOF'
<what changed in generated projects, and any manual steps after `copier update`>
EOF
git fetch --tags
```

`--target` needs a branch name or a **full** SHA. A short SHA fails with `HTTP 422 ... tag_name is not a valid tag`. Push first, so `main` on GitHub is the commit you mean to tag.

Release notes are for people running `copier update`: list what changes in their projects, and call out anything that needs action (conflicts to expect, renamed answers, new required tools).

### 5. Check that Copier serves it

From a scratch directory, never inside the repo:

```bash
uvx copier copy --defaults --skip-tasks gh:samizdata-co/maia <scratch>/release-check
```

Look for `Copying from template version X.Y.Z` and `_commit: vX.Y.Z` in the generated `.copier-answers.yml`, and spot-check the files you changed. For risky changes, also check an update. Generate a project from the previous tag (`--vcs-ref vPREV`), `git init` and commit it, then run `uvx copier update --defaults --skip-tasks` and check the diff.

## Brand extension updates

The SAMIZDATA Quarto extension is vendored into `template/_extensions/samizdata-co/samizdata`. To bump it:

```bash
cd template && quarto update extension samizdata-co/brand@<tag>
```

Then update the pinned version in `test_project_vendors_single_pinned_brand` and the version link in README.md, and release as a minor version. This is the main reason the template moved to Copier: existing projects pick up brand updates with `copier update`.

## Things that trip people up

- Copier refuses to run `_tasks` without `--trust`. Use `--skip-tasks` in checks that don't need them.
- The project slug defaults to the destination folder name and must be at least 2 characters (`[a-zA-Z0-9][-_a-zA-Z0-9]+`), so scratch folders like `w` fail validation.
- `copier update` only works in a git repo with a clean working tree, and only for projects created with Copier. Projects made with the old Cookiecutter version have no answers file.
