"""The API smoke test must not rebuild the developer's default catalog."""

from pathlib import Path

root = Path(__file__).resolve().parents[1]
smoke = (root / "tests" / "api_smoke.py").read_text()
bootstrap = (root / "scripts" / "bootstrap_db.py").read_text()

assert "TemporaryDirectory" in smoke
assert '"--database"' in smoke
assert '"--database"' in bootstrap

print("API smoke database isolation passed")
