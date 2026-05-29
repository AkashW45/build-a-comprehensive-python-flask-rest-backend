import os
import sys
from unittest.mock import patch, MagicMock
import pytest
from flask import Flask, Blueprint

# We'll import create_app later, after mocking the employee_routes module to avoid import errors
# in the test environment.

@pytest.fixture
def mock_employee_bp():
    """A minimal valid Blueprint to stand in for the real employee_bp."""
    return Blueprint('employee', __name__)

@pytest.fixture
def app(mock_employee_bp):
    """Create the Flask app with mocked dependencies."""
    # Mock the entire package tree so `from src.routes.employee_routes import employee_bp` works
    with patch.dict(sys.modules, {
        'src': MagicMock(),
        'src.routes': MagicMock(),
        'src.routes.employee_routes': MagicMock()
    }):
        sys.modules['src.routes.employee_routes'].employee_bp = mock_employee_bp

        # Now import the application factory
        from employee_service.app import create_app  # adjust to actual module path if needed
        application = create_app()
        application.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # avoid real DB
        })
        yield application

@pytest.fixture
def client(app):
    return app.test_client()


# ------------------------------------------------------------------ Tests

def test_create_app_returns_flask_app(app):
    """Happy path: factory returns a valid Flask instance."""
    assert isinstance(app, Flask)

def test_health_endpoint_returns_ok(client):
    """Happy path: /health returns status ok."""
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.get_json() == {'status': 'ok'}

def test_default_database_url():
    """If no env variable is set, SQLALCHEMY_DATABASE_URI is the default PostgreSQL string."""
    with patch.dict(os.environ, {}, clear=True):
        with patch.dict(sys.modules, {
            'src': MagicMock(), 'src.routes': MagicMock(),
            'src.routes.employee_routes': MagicMock()
        }):
            sys.modules['src.routes.employee_routes'].employee_bp = Blueprint('e', __name__)
            from employee_service.app import create_app
            app = create_app()
            expected = 'postgresql://user:pass@localhost:5432/employees'
            assert app.config['SQLALCHEMY_DATABASE_URI'] == expected

def test_custom_database_url_via_env():
    """Edge case: custom DATABASE_URL environment variable overrides the default."""
    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://custom:5432/testdb'}, clear=True):
        with patch.dict(sys.modules, {
            'src': MagicMock(), 'src.routes': MagicMock(),
            'src.routes.employee_routes': MagicMock()
        }):
            sys.modules['src.routes.employee_routes'].employee_bp = Blueprint('e', __name__)
            from employee_service.app import create_app
            app = create_app()
            assert 'postgresql://custom:5432/testdb' in app.config['SQLALCHEMY_DATABASE_URI']

def test_employee_blueprint_registered(app):
    """Edge case: the employee blueprint is correctly registered with /employees prefix."""
    # Blueprint will be visible in app.blueprints
    assert 'employee' in app.blueprints
    # The url_prefix should be enforced by register_blueprint
    # We can verify by checking the registered rules (optional)
    rule_paths = [rule.rule for rule in app.url_map.iter_rules()]
    # At least one rule should start with /employees
    assert any('/employees' in path for path in rule_paths)

def test_extensions_initialized(app):
    """The extensions (db, migrate, ma) are bound to the app."""
    from employee_service.app import db, migrate, ma
    # SQLAlchemy, Migrate, Marshmallow are registered in app.extensions
    assert 'sqlalchemy' in app.extensions
    assert 'migrate' in app.extensions
    assert 'flask-marshmallow' in app.extensions