import pytest
from app import create_app, db
from src.models.employee import Employee

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_create_employee(client):
    response = client.post('/employees', json={'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com', 'department_id': 1, 'role': 'employee'})
    assert response.status_code == 201
    assert response.json['email'] == 'john@example.com'

def test_get_employees(client):
    # Create a test employee
    client.post('/employees', json={'first_name': 'Jane', 'last_name': 'Doe', 'email': 'jane@example.com', 'department_id': 1, 'role': 'employee'})
    response = client.get('/employees')
    assert response.status_code == 200
    assert len(response.json['employees']) == 1

def test_search(client):
    client.post('/employees', json={'first_name': 'Alice', 'last_name': 'Smith', 'email': 'alice@example.com', 'department_id': 1, 'role': 'employee'})
    response = client.get('/employees/search?q=Alice')
    assert response.status_code == 200
    assert len(response.json) == 1
