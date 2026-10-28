import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GenerationTests(unittest.TestCase):
    def generate(self) -> Path:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary)
        slug = 'plain-test'
        subprocess.run(
            [
                'uvx', 'cookiecutter', str(ROOT), '--no-input',
                'project_name=Generated Test', f'project_slug={slug}',
                'notebook=None', 'language=None', 'virtual_env=None',
            ],
            cwd=temporary,
            check=True,
        )
        return temporary / slug

    def test_plain_project_has_no_node_files(self):
        project = self.generate()
        self.assertFalse((project / 'visuals').exists())
        self.assertFalse((project / 'package.json').exists())

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


if __name__ == '__main__':
    unittest.main()
