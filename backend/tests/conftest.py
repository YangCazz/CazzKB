import pytest
import os
from pathlib import Path

# Load local .env file if it exists (for API keys, etc.)
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path, override=False)

os.environ["CAZZKB_DB_PATH"] = ":memory:"


@pytest.fixture(autouse=True)
def setup_db():
    from app.models.db import db, init_db
    db.init(":memory:")
    init_db()
    yield
    db.close()
