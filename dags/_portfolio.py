import os
import sys
from pathlib import Path


def repo_root():
    return Path(os.getenv("PORTFOLIO_REPO_ROOT", Path(__file__).resolve().parents[1]))


def add_project_scripts(project_name):
    scripts_path = repo_root() / project_name / "scripts"
    sys.path.insert(0, str(scripts_path))
    return scripts_path

