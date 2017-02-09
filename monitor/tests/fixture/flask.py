# coding=utf-8
import pytest


@pytest.fixture(scope='session', autouse=True)
def app():
    from app import create_app
    app = create_app()
    ctx = app.test_request_context()
    with ctx:
        yield app


@pytest.fixture
def rollback():
    from app import db
    db.session.begin(subtransactions=True)
    try:
        yield
    finally:
        db.session.rollback()
        db.session.remove()
