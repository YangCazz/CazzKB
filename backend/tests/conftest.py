import pytest
import os

os.environ["CAZZKB_DB_PATH"] = ":memory:"


@pytest.fixture(autouse=True)
def setup_db():
    from app.models.db import db, init_db
    db.init(":memory:")
    init_db()
    yield
    db.close()
