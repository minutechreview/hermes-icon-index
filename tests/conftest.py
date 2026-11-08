"""Load the plugin directory as an importable package named `icon_index`."""

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load():
    if "icon_index" in sys.modules:
        return sys.modules["icon_index"]
    spec = importlib.util.spec_from_file_location(
        "icon_index", ROOT / "__init__.py", submodule_search_locations=[str(ROOT)]
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["icon_index"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def plugin():
    return _load()
