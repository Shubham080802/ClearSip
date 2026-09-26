"""Recompute the transparent label assessments after a policy or label update."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.classification import refresh_assessments

refresh_assessments(ROOT / "data" / "clearsip.db")
print("Rebuilt label assessments")
