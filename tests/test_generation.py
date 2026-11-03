import json
import shutil
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GenerationTests(unittest.TestCase):
    def generate(self, *data: str, slug: str = 'plain-test', check: bool = True):
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary)
        args = ['project_name=Generated Test', f'project_slug={slug}', *data]
        result = subprocess.run(
            [
                'uvx', 'copier', 'copy', '--defaults', '--skip-tasks',
                '--vcs-ref', 'HEAD', str(ROOT), str(temporary / 'project'),
                *(item for arg in args for item in ('--data', arg)),
            ],
            capture_output=True,
            text=True,
        )
        if check:
            self.assertEqual(result.returncode, 0, result.stderr)
            return temporary / 'project'
        return result

    def test_plain_project_has_no_node_files(self):
        project = self.generate()
        self.assertFalse((project / 'visuals').exists())
        self.assertFalse((project / 'package.json').exists())

    def test_plain_project_has_no_optional_files(self):
        project = self.generate()
        self.assertEqual(sorted(p.name for p in (project / 'notebooks').iterdir()), ['.gitkeep'])
        self.assertFalse((project / 'pyproject.toml').exists())
        self.assertFalse(list(project.glob('*.Rproj')))

    def test_project_records_answers(self):
        project = self.generate()
        answers = (project / '.copier-answers.yml').read_text()
        self.assertIn('project_slug: plain-test', answers)
        self.assertIn('_src_path:', answers)

    def test_r_quarto_project(self):
        project = self.generate('language=[R]', 'notebook=Quarto')
        self.assertTrue((project / 'plain-test.Rproj').is_file())
        analysis = (project / 'notebooks/analysis.qmd').read_text()
        self.assertIn('title: "Analysis: Generated Test"', analysis)
        self.assertIn('library(tidyverse)', analysis)
        self.assertNotIn('import pandas', analysis)
        self.assertFalse((project / 'notebooks/analysis.ipynb').exists())

    def test_python_jupyter_uv_project(self):
        project = self.generate('language=[Python]', 'notebook=Jupyter', 'virtual_env=uv')
        self.assertIn('name = "plain-test"', (project / 'pyproject.toml').read_text())
        self.assertIn('!uv pip install pandas', (project / 'notebooks/analysis.ipynb').read_text())
        self.assertFalse(list(project.glob('*.Rproj')))

    def test_observable_project(self):
        project = self.generate('notebook=Observable')
        self.assertTrue((project / 'package.json').is_file())
        self.assertIn('Analysis: Generated Test', (project / 'notebooks/analysis.onb.html').read_text())

    def test_rendered_text_has_no_template_tags(self):
        project = self.generate('language=[R, Python]', 'notebook=Quarto')
        for name in ('README.md', 'story.md', 'hours.klg', 'LICENSE', 'notebooks/analysis.qmd'):
            text = (project / name).read_text()
            self.assertNotIn('{{', text, name)
            self.assertNotIn('{%', text, name)

    def test_licence_names_project_and_author(self):
        project = self.generate()
        licence = (project / 'LICENSE').read_text()
        year = date.today().year
        self.assertIn('Generated Test: A short description of the project.', licence)
        self.assertIn(f'Copyright (C) {year}  Nicu Calcea', licence)
        self.assertIn(f'Generated Test  Copyright (C) {year}  Nicu Calcea', licence)
        self.assertNotIn('<name of author>', licence)

    def test_invalid_slug_is_rejected(self):
        result = self.generate(slug='not a slug', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Use letters, numbers, hyphens and underscores only', result.stderr)

    def test_project_vendors_single_pinned_brand(self):
        project = self.generate()
        extension = project / '_extensions/samizdata-co/samizdata'
        self.assertTrue((extension / '_brand.yml').is_file())
        self.assertTrue((extension / 'assets/logos/mark.svg').is_file())
        self.assertFalse((project / '_brand.yml').exists())
        self.assertIn('version: 0.1.0', (extension / '_extension.yml').read_text())
        quarto = (project / '_quarto.yml').read_text()
        self.assertNotIn('brand: _brand.yml', quarto)
        self.assertTrue((project / 'fonts/SpaceGrotesk-Variable.ttf').is_file())
        self.assertTrue((project / 'fonts/WorkSans-Variable.ttf').is_file())
        self.assertIn('include-in-header: samizdata-pdf.tex', quarto)
        self.assertFalse((project / '_extensions/ziaruldegarda').exists())

    def test_zdg_project_vendors_zdg_brand(self):
        project = self.generate('outlet=zdg')
        extension = project / '_extensions/ziaruldegarda/zdg'
        self.assertTrue((extension / '_brand.yml').is_file())
        self.assertTrue((extension / 'assets/logos/logo.svg').is_file())
        self.assertIn('version: 0.1.0', (extension / '_extension.yml').read_text())
        quarto = (project / '_quarto.yml').read_text()
        self.assertIn('include-in-header: zdg-pdf.tex', quarto)
        self.assertNotIn('samizdata', quarto)
        self.assertTrue((project / 'zdg-pdf.tex').is_file())
        self.assertFalse((project / '_extensions/samizdata-co').exists())
        self.assertFalse((project / 'fonts').exists())
        self.assertFalse((project / 'samizdata-pdf.tex').exists())
        self.assertIn('Ziarul de Gardă report styling', (project / 'README.md').read_text())

    def test_project_without_outlet_has_no_brand(self):
        project = self.generate('outlet=none')
        self.assertFalse((project / '_extensions').exists())
        self.assertFalse((project / 'fonts').exists())
        self.assertEqual(sorted(p.name for p in project.glob('*.tex')), [])
        quarto = (project / '_quarto.yml').read_text()
        self.assertNotIn('include-in-header', quarto)
        self.assertNotIn('report styling', (project / 'README.md').read_text())

    def test_plain_project_has_no_charts(self):
        project = self.generate()
        self.assertFalse((project / 'charts').exists())
        self.assertFalse((project / '.claude').exists())

    def test_mozaic_charts_use_the_outlet_theme(self):
        for outlet, export in (('samizdata', 'samizdata'), ('zdg', 'zdg')):
            with self.subTest(outlet=outlet):
                project = self.generate(f'outlet={outlet}', 'charts=mozaic')
                charts = project / 'charts'
                theme = (charts / 'src/lib/theme.ts').read_text()
                self.assertIn(f"export {{ {export} as theme }} from './brands/{outlet}/theme.js';", theme)
                brand = (charts / f'src/lib/brands/{outlet}/theme.ts').read_text()
                self.assertIn(f'export const {export} = extendTheme(', brand)
                self.assertTrue((charts / f'src/lib/brands/{outlet}/logo.ts').is_file())
                self.assertEqual(len(list((charts / 'src/lib/brands').iterdir())), 1)

    def test_mozaic_charts_project(self):
        project = self.generate('outlet=zdg', 'charts=mozaic')
        charts = project / 'charts'
        package = json.loads((charts / 'package.json').read_text())
        self.assertEqual(package['name'], 'plain-test-charts')
        self.assertEqual(package['dependencies']['mozaic'], 'link:../../mozaic/packages/mozaic')
        self.assertEqual(package['devDependencies']['@mozaic/cli'], 'link:../../mozaic/packages/cli')
        config = (charts / 'mozaic.config.ts').read_text()
        self.assertIn("project: 'plain-test'", config)
        self.assertIn("locales: ['ro', 'ru'] as LocaleCode[]", config)
        self.assertTrue((charts / 'data/example.csv').is_file())
        self.assertTrue((charts / 'src/charts/example/Chart.svelte').is_file())
        self.assertTrue((charts / 'src/routes/embed/[chart]/[locale]/+page.svelte').is_file())
        self.assertIn('{#snippet children(plot)}', (charts / 'AGENTS.md').read_text())
        self.assertTrue((project / '.claude/skills/mozaic-chart/SKILL.md').is_file())
        self.assertIn('## Charts', (project / 'README.md').read_text())
        # The root .gitignore must not hide the charts' src/lib.
        self.assertIn('/lib/', (project / '.gitignore').read_text().splitlines())

    def test_mozaic_charts_without_outlet_use_base(self):
        project = self.generate('outlet=none', 'charts=mozaic', 'chart_locales=en,ro', 'mozaic_path=/opt/mozaic')
        charts = project / 'charts'
        theme = (charts / 'src/lib/theme.ts').read_text()
        self.assertIn("extendTheme({ name: 'plain-test', label: 'Generated Test' })", theme)
        self.assertFalse((charts / 'src/lib/brands').exists())
        package = json.loads((charts / 'package.json').read_text())
        self.assertEqual(package['dependencies']['mozaic'], 'link:/opt/mozaic/packages/mozaic')
        self.assertIn("locales: ['en', 'ro']", (charts / 'mozaic.config.ts').read_text())

    def test_invalid_chart_locale_is_rejected(self):
        result = self.generate('charts=mozaic', 'chart_locales=en,fr', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Use en, ro and ru', result.stderr)

    def test_vendored_mozaic_themes_match_brands(self):
        brands = {
            'samizdata': ROOT.parent / 'samizdata/brand/datavis/mozaic',
            'zdg': ROOT.parent / 'ziaruldegarda/brand/datavis/mozaic',
        }
        for outlet, source in brands.items():
            if not source.is_dir():
                continue
            vendored = next((ROOT / 'template').glob(f"*charts*/src/lib/*brands*/*'{outlet}'*"))
            for file in ('theme.ts', 'logo.ts'):
                with self.subTest(outlet=outlet, file=file):
                    self.assertEqual((vendored / file).read_text(), (source / file).read_text())


if __name__ == '__main__':
    unittest.main()
