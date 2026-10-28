from pathlib import Path
import os

# Configure R
if "R" not in "{{ cookiecutter.language }}":
    # Path(".Rprofile").unlink()
    Path("{{cookiecutter.project_slug}}.Rproj").unlink()


# Configure Quarto
if "{{ cookiecutter.notebook }}" != "Quarto":
    Path("notebooks/analysis.qmd").unlink()

# Configure Jupyter
if "{{ cookiecutter.notebook }}" != "Jupyter":
    Path("notebooks/analysis.ipynb").unlink()

# Configure Observable
if "{{ cookiecutter.notebook }}" == "Observable":
    os.system('npm install')
else:
    Path("notebooks/analysis.onb.html").unlink()
    Path("package.json").unlink()


# Set up uv
if "{{ cookiecutter.virtual_env }}" == "uv":
    os.system('uv venv')
    if "{{ cookiecutter.notebook }}" == "Jupyter":
        os.system('uv add --dev ipykernel')
else:
    Path("pyproject.toml").unlink()