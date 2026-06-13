def test_import_app():
    from app.main import app

    assert app is not None


def test_app_is_fastapi():
    from app.main import app
    from fastapi import FastAPI

    assert isinstance(app, FastAPI)


def test_app_title():
    from app.main import app

    assert app.title is not None and len(app.title) > 0
