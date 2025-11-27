"""Pytest configuration and fixtures for Elder tests."""

import pytest

from apps.api.main import create_app
from shared.database import db as _db


@pytest.fixture(scope="session")
def app():
    """
    Create Flask application for testing.

    Returns:
        Flask app configured for testing
    """
    app = create_app("testing")

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """
    Create Flask test client.

    Args:
        app: Flask application fixture

    Returns:
        Flask test client
    """
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    """
    Provide database session for tests with transaction rollback.

    Args:
        app: Flask application fixture

    Yields:
        SQLAlchemy database session
    """
    with app.app_context():
        _db.session.begin_nested()
        yield _db
        _db.session.rollback()
        _db.session.remove()
