import pytest
from unittest.mock import patch, MagicMock
import json
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
import sys

# Mock the 'app' module before importing the auth routes.
sys.modules['app'] = MagicMock()
sys.modules['app'].db = MagicMock()
sys.modules['app'].jwt = MagicMock()

from src.routes import auth_routes


def generate_token(app, identity, claims=None):
    """Helper to create a valid JWT for testing protected endpoints."""
    with app.app_context():
        return create_access_token(identity=identity, additional_claims=claims or {})


@pytest.fixture
def app():
    """Flask application with the auth blueprint and JWT configured."""
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'super-secret'
    app.config['TESTING'] = True

    real_jwt = JWTManager(app)

    # Replace the blueprint's mocked jwt with the real one and register the loaders.
    auth_routes.jwt = real_jwt
    real_jwt.user_identity_loader(auth_routes.user_identity_lookup)
    real_jwt.user_lookup_loader(auth_routes.user_lookup_callback)

    app.register_blueprint(auth_routes.auth_bp)
    return app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def mock_user():
    """A minimal mocked User object."""
    user = MagicMock()
    user.id = 1
    user.username = 'testuser'
    user.email = 'test@example.com'
    user.role = 'employee'
    user.mfa_enabled = False
    user.check_password = MagicMock()
    user.set_password = MagicMock()
    return user


class TestRegister:
    def test_register_success(self, client, mock_user):
        """Happy path: register a new user."""
        with patch('src.routes.auth_routes.User') as mock_user_cls, \
             patch('src.routes.auth_routes.db') as mock_db:
            mock_user_cls.query.filter_by.return_value.first.return_value = None
            mock_user_cls.return_value = mock_user

            data = {"username": "newuser", "email": "new@example.com", "password": "pass"}
            resp = client.post('/register', json=data)

            assert resp.status_code == 201
            assert resp.get_json()['msg'] == 'User created'
            mock_db.session.add.assert_called_once_with(mock_user)
            mock_db.session.commit.assert_called_once()
            mock_user.set_password.assert_called_once_with('pass')

    def test_register_username_exists(self, client):
        """Error path: duplicate username returns 409."""
        with patch('src.routes.auth_routes.User') as mock_user_cls, \
             patch('src.routes.auth_routes.db'):
            mock_user_cls.query.filter_by.return_value.first.return_value = MagicMock()

            resp = client.post('/register', json={"username": "exists", "email": "e@e.com", "password": "pwd"})
            assert resp.status_code == 409
            assert resp.get_json()['msg'] == 'Username already exists'

    def test_register_missing_username(self, client):
        """Edge case: missing 'username' in request body causes a 500 error."""
        resp = client.post('/register', json={"email": "e@e.com", "password": "pwd"})
        assert resp.status_code == 500


class TestLogin:
    def test_login_success_no_mfa(self, client, mock_user):
        """Happy path: successful login without MFA."""
        with patch('src.routes.auth_routes.User') as mock_user_cls:
            mock_user_cls.query.filter_by.return_value.first.return_value = mock_user
            mock_user.check_password.return_value = True
            mock_user.mfa_enabled = False

            resp = client.post('/login', json={"username": "testuser", "password": "correct"})
            assert resp.status_code == 200
            data = resp.get_json()
            assert 'access_token' in data
            assert 'refresh_token' in data

    def test_login_mfa_required(self, client, mock_user):
        """Happy path: login with MFA enabled returns a temporary token."""
        with patch('src.routes.auth_routes.User') as mock_user_cls:
            mock_user_cls.query.filter_by.return_value.first.return_value = mock_user
            mock_user.check_password.return_value = True
            mock_user.mfa_enabled = True

            resp = client.post('/login', json={"username": "testuser", "password": "pass"})
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['mfa_required'] is True
            assert 'temp_token' in data

    def test_login_invalid_credentials(self, client):
        """Error path: user not found returns 401."""
        with patch('src.routes.auth_routes.User') as mock_user_cls:
            mock_user_cls.query.filter_by.return_value.first.return_value = None
            resp = client.post('/login', json={"username": "nouser", "password": "x"})
            assert resp.status_code == 401
            assert resp.get_json()['msg'] == 'Invalid credentials'

    def test_login_wrong_password(self, client, mock_user):
        """Error path: wrong password returns 401."""
        with patch('src.routes.auth_routes.User') as mock_user_cls:
            mock_user_cls.query.filter_by.return_value.first.return_value = mock_user
            mock_user.check_password.return_value = False
            resp = client.post('/login', json={"username": "testuser", "password": "bad"})
            assert resp.status_code == 401

    def test_login_missing_username(self, client):
        """Edge case: missing 'username' in request body causes 500."""
        resp = client.post('/login', json={"password": "x"})
        assert resp.status_code == 500


class TestVerifyMFA:
    @pytest.fixture(autouse=True)
    def _setup_token(self, app):
        """Create a valid JWT for the MFA tests."""
        self.token = generate_token(app, 1, {'role': 'employee'})

    def test_verify_mfa_success(self, client, app, mock_user):
        """Happy path: correct MFA code returns new access and refresh tokens."""
        with patch('src.routes.auth_routes.pyotp.TOTP') as mock_totp_class, \
             patch('src.routes.auth_routes.MFA') as mock_mfa_cls, \
             patch('src.routes.auth_routes.User') as mock_user_cls:
            mock_mfa_cls.query.filter_by.return_value.first.return_value = MagicMock(secret='secret')
            mock_totp_instance = MagicMock()
            mock_totp_instance.verify.return_value = True
            mock_totp_class.return_value = mock_totp_instance
            mock_user_cls.query.get.return_value = mock_user

            headers = {'Authorization': f'Bearer {self.token}'}
            resp = client.post('/mfa/verify', json={"code": "123456"}, headers=headers)

            assert resp.status_code == 200
            data = resp.get_json()
            assert 'access_token' in data
            assert 'refresh_token' in data

    def test_verify_mfa_invalid_code(self, client):
        """Error path: invalid MFA code returns 401."""
        with patch('src.routes.auth_routes.pyotp.TOTP') as mock_totp_class, \
             patch('src.routes.auth_routes.MFA') as mock_mfa_cls:
            mock_mfa_cls.query.filter_by.return_value.first.return_value = MagicMock(secret='secret')
            mock_totp_instance = MagicMock()
            mock_totp_instance.verify.return_value = False
            mock_totp_class.return_value = mock_totp_instance

            resp = client.post('/mfa/verify', json={"code": "wrong"},
                                headers={'Authorization': f'Bearer {self.token}'})
            assert resp.status_code == 401
            assert resp.get_json()['msg'] == 'Invalid code'

    def test_verify_mfa_no_mfa_configured(self, client):
        """Error path: MFA not configured returns 400."""
        with patch('src.routes.auth_routes.MFA') as mock_mfa_cls:
            mock_mfa_cls.query.filter_by.return_value.first.return_value = None
            resp = client.post('/mfa/verify', json={"code": "123456"},
                                headers={'Authorization': f'Bearer {self.token}'})
            assert resp.status_code == 400
            assert resp.get_json()['msg'] == 'MFA not configured'

    def test_verify_mfa_missing_code(self, client):
        """Edge case: missing 'code' in request body causes 500."""
        resp = client.post('/mfa/verify', json={},
                            headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 500

    def test_verify_mfa_no_token(self, client):
        """Error path: missing JWT returns 401."""
        resp = client.post('/mfa/verify', json={"code": "123456"})
        assert resp.status_code == 401


class TestSetupMFA:
    @pytest.fixture(autouse=True)
    def _setup_token(self, app):
        self.token = generate_token(app, 1, {'role': 'employee'})

    def test_setup_mfa_success(self, client, app, mock_user):
        """Happy path: setup MFA returns secret and QR URL."""
        with patch('src.routes.auth_routes.pyotp.random_base32', return_value='test_secret'):
            with patch('src.routes.auth_routes.pyotp.totp.TOTP') as mock_totp_class:
                mock_totp_instance = MagicMock()
                mock_totp_instance.provisioning_uri.return_value = 'otpauth://...'
                mock_totp_class.return_value = mock_totp_instance

                with patch('src.routes.auth_routes.MFA') as mock_mfa_cls, \
                     patch('src.routes.auth_routes.User') as mock_user_cls, \
                     patch('src.routes.auth_routes.db') as mock_db:
                    mock_user_cls.query.get.return_value = mock_user

                    resp = client.post('/mfa/setup', json={},
                                        headers={'Authorization': f'Bearer {self.token}'})
                    assert resp.status_code == 201
                    data = resp.get_json()
                    assert data['secret'] == 'test_secret'
                    assert data['qr_url'] == 'otpauth://...'
                    mock_db.session.add.assert_called_once()
                    mock_db.session.commit.assert_called_once()

    def test_setup_mfa_no_token(self, client):
        """Error path: missing JWT returns 401."""
        resp = client.post('/mfa/setup', json={})
        assert resp.status_code == 401


def test_sso_login(client):
    """SSO login always returns 501 (not implemented)."""
    resp = client.post('/sso/login', json={})
    assert resp.status_code == 501
    assert resp.get_json()['msg'] == 'SAML SSO flow not yet implemented'


def test_user_identity_lookup():
    """Unit test: user identity loader returns the given user_id."""
    result = auth_routes.user_identity_lookup(42)
    assert result == 42


def test_user_lookup_callback():
    """Unit test: user lookup callback returns the user object from DB."""
    with patch('src.routes.auth_routes.User') as mock_user_cls:
        mock_user = MagicMock()
        mock_user_cls.query.get.return_value = mock_user

        result = auth_routes.user_lookup_callback({}, {'sub': 42})
        assert result == mock_user
        mock_user_cls.query.get.assert_called_with(42)