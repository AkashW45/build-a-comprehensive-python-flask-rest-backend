import pytest
import json
from app import app, db
from src.models.employee import Employee


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


@pytest.fixture
def sample_employee(client):
    employee = Employee(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        active=True,
        department='Engineering',
        role='Developer'
    )
    db.session.add(employee)
    db.session.commit()
    return employee


def test_get_employees_paginated(client, sample_employee):
    response = client.get('/employees?page=1&per_page=10')
    assert response.status_code == 200
    data = response.get_json()
    assert 'employees' in data
    assert len(data['employees']) == 1
    assert data['total'] == 1
    assert data['employees'][0]['first_name'] == 'John'


def test_get_employee_found(client, sample_employee):
    response = client.get(f'/employees/{sample_employee.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == sample_employee.id
    assert data['first_name'] == 'John'


def test_get_employee_not_found(client):
    response = client.get('/employees/999')
    assert response.status_code == 404


def test_create_employee(client):
    new_employee = {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane.smith@example.com',
        'active': True,
        'department': 'Marketing',
        'role': 'Manager'
    }
    response = client.post('/employees',
                           data=json.dumps(new_employee),
                           content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert data['first_name'] == 'Jane'
    assert data['email'] == 'jane.smith@example.com'
    # Verify persisted in database
    employee = Employee.query.get(data['id'])
    assert employee is not None


def test_update_employee(client, sample_employee):
    update_data = {'first_name': 'Johnny', 'last_name': 'Doe'}
    response = client.put(f'/employees/{sample_employee.id}',
                          data=json.dumps(update_data),
                          content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['first_name'] == 'Johnny'
    # Check database
    updated = Employee.query.get(sample_employee.id)
    assert updated.first_name == 'Johnny'


def test_delete_employee(client, sample_employee):
    response = client.delete(f'/employees/{sample_employee.id}')
    assert response.status_code == 204
    # Verify deletion
    assert Employee.query.get(sample_employee.id) is None


def test_search_employees(client, sample_employee):
    # Search with a valid query
    response = client.get('/search?q=John')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['first_name'] == 'John'

    # Empty query returns empty list
    response = client.get('/search?q=')
    assert response.status_code == 200
    data = response.get_json()
    assert data == []