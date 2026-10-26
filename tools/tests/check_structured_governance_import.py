"""Load the hyphenated native structured-governance checker for tests."""

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

_PATH = TOOLS / "check-structured-governance.py"
_SPEC = importlib.util.spec_from_file_location("check_structured_governance", _PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"cannot load {_PATH}")
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)

load_structured_governance = _MODULE.load_structured_governance
