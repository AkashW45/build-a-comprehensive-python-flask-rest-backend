import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login(client):
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'password'})
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_invalid(client):
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'wrong'})
    assert response.status_code == 401

def test_refresh(client):
    # First obtain tokens
    login_resp = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'password'})
    refresh_token = login_resp.json['refresh_token']
    response = client.post('/api/v1/auth/refresh', headers={'Authorization': f'Bearer {refresh_token}'})
    assert response.status_code == 200
    assert 'access_token' in response.json
