import json
import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_refresh_token

from api_gateway.src.routes.auth_routes import auth_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test-secret"
    app.config["TESTING"] = True
    JWTManager(app)
    app.register_blueprint(auth_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_login_success(client):
    resp = client.post('/login', json={'username': 'admin', 'password': 'password'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data


def test_login_invalid_credentials(client):
    resp = client.post('/login', json={'username': 'admin', 'password': 'wrong'})
    assert resp.status_code == 401
    data = resp.get_json()
    assert 'msg' in data
    assert data['msg'] == 'Invalid credentials'


def test_login_missing_username(client):
    resp = client.post('/login', json={'password': 'password'})
    assert resp.status_code == 401


def test_refresh_success(app, client):
    with app.app_context():
        refresh_token = create_refresh_token(identity='admin')
    headers = {'Authorization': f'Bearer {refresh_token}'}
    resp = client.post('/refresh', headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'access_token' in data


def test_refresh_invalid_token(client):
    headers = {'Authorization': 'Bearer invalidtoken'}
    resp = client.post('/refresh', headers=headers)
    assert resp.status_code == 401


def test_verify_mfa(client):
    resp = client.post('/mfa/verify')
    assert resp.status_code == 200
    assert resp.get_json() == {'msg': 'MFA verified'}