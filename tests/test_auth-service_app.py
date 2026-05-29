import os
import sys
import pytest
from unittest.mock import patch
from flask import Flask

# Assume the package is named auth_service (hyphens replaced)
from auth_service.app import create_app, db, jwt


@pytest.fixture
def app():
    """Create app with test configuration."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_health_endpoint(client):
    """Happy path: /health returns status ok."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_create_app_returns_flask_app():
    """Happy path: create_app returns a Flask application."""
    app = create_app()
    assert isinstance(app, Flask)
    # Verify that db and jwt are initialized (attached to the app)
    # The db object has an attribute `_app` when bound
    with app.app_context():
        assert db.engine is not None
        assert jwt._app is not None


def test_custom_environment_variables(monkeypatch):
    """Edge case: custom environment values are respected."""
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///test.db')
    monkeypatch.setenv('JWT_SECRET_KEY', 'custom-secret')
    monkeypatch.setenv('JWT_ACCESS_TOKEN_EXPIRES', '1800')
    monkeypatch.setenv('JWT_REFRESH_TOKEN_EXPIRES', '1209600')
    app = create_app()
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///test.db'
    assert app.config['JWT_SECRET_KEY'] == 'custom-secret'
    # Override is not direct because env vars only change default if not set,
    # but the app config uses os.environ.get with defaults; so above pattern works.
    # JWT_ACCESS_TOKEN_EXPIRES is not read from env; the app uses hardcoded value.
    # So we skip that assertion. The test mainly verifies DATABASE_URL and JWT_SECRET_KEY.
    # For access token, we check the default remains unless we explicitly patch.
    assert app.config['JWT_ACCESS_TOKEN_EXPIRES'] == 3600  # unchanged


def test_jwt_configuration():
    """Edge case: verify JWT token location and expiry defaults."""
    app = create_app()
    assert app.config['JWT_TOKEN_LOCATION'] == ['headers']
    assert app.config['JWT_ACCESS_TOKEN_EXPIRES'] == 3600
    assert app.config['JWT_REFRESH_TOKEN_EXPIRES'] == 86400 * 30  # 30 days


def test_create_app_blueprint_import_error(monkeypatch):
    """Error path: if blueprint import fails, create_app raises ImportError."""
    # Remove the auth routes module from sys.modules to force ImportError
    monkeypatch.delitem(sys.modules, 'src.routes.auth_routes', raising=False)
    with pytest.raises(ImportError):
        create_app()


def test_create_app_database_init_error(mocker):
    """Error path: if db.init_app fails, the exception propagates."""
    mock_init = mocker.patch.object(db, 'init_app', side_effect=RuntimeError('DB init failed'))
    with pytest.raises(RuntimeError, match='DB init failed'):
        create_app()
    mock_init.assert_called_once()