from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_adf_export.py"


def test_adf_export_validation_passes(capsys):
    spec = importlib.util.spec_from_file_location("validate_adf_export", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    module.main()
    captured = capsys.readouterr()
    assert "ADF export validation passed." in captured.out
