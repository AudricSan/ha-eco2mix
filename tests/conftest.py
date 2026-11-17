"""Charge jp_parser.py directement (sans importer le paquet, donc sans Home Assistant)."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
_spec = spec_from_file_location(
    "jp_parser", ROOT / "custom_components" / "eco2mix" / "jp_parser.py"
)
jp_parser = module_from_spec(_spec)
sys.modules["jp_parser"] = jp_parser
_spec.loader.exec_module(jp_parser)
