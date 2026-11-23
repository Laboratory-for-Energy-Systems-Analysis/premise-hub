"""Reuse SETAC display code with an independent result reader and caches."""

from importlib import util
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(component, **initial):
    path = ROOT.parent / "setac_2026" / f"{component}.py"
    spec = util.spec_from_file_location(f"apps.mcv_2026._{component}", path)
    module = util.module_from_spec(spec)
    vars(module).update(initial)
    spec.loader.exec_module(module)
    return module
