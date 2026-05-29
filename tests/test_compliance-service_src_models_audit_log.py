import pytest
from datetime import datetime, timezone
from app import db
from flask import Flask
from models.audit_log import AuditLog
import sys
import os

# Ensure the package path is set correctly; adjust as needed for your project structure.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../compliance-service/src')))

@pytest.fixture(scope='function')
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def session(app):
    with app.app_context():
        yield db.session

def test_create_audit_log_happy_path(session):
    """Happy path: create an AuditLog entry with all fields and verify persistence."""
    log = AuditLog(
        user_id=42,
        action='CREATE_EMPLOYEE',
        resource_type='Employee',
        resource_id=101,
        before_state=None,
        after_state={'id': 101, 'name': 'John'},
        ip_address='192.168.0.1'
    )
    session.add(log)
    session.commit()

    saved_log = AuditLog.query.first()
    assert saved_log.id is not None
    assert saved_log.user_id == 42
    assert saved_log.action == 'CREATE_EMPLOYEE'
    assert saved_log.resource_type == 'Employee'
    assert saved_log.resource_id == 101
    assert saved_log.before_state is None
    assert saved_log.after_state == {'id': 101, 'name': 'John'}
    assert saved_log.ip_address == '192.168.0.1'
    assert isinstance(saved_log.timestamp, datetime)

def test_audit_log_timestamp_auto_set(session):
    """Edge case: verify timestamp is auto-set on creation."""
    before = datetime.utcnow()
    log = AuditLog(user_id=1, action='TEST')
    session.add(log)
    session.commit()
    after = datetime.utcnow()
    assert before <= log.timestamp <= after

def test_audit_log_missing_required_fields_raises_error(session):
    """Error path: missing required fields should raise IntegrityError."""
    log1 = AuditLog(action='TEST')
    session.add(log1)
    with pytest.raises(Exception):
        session.commit()
    session.rollback()

    log2 = AuditLog(user_id=1)
    session.add(log2)
    with pytest.raises(Exception):
        session.commit()
    session.rollback()

def test_audit_log_max_string_lengths(session):
    """Edge case: string fields at max length."""
    max_action = 'A' * 100
    max_resource_type = 'B' * 50
    max_ip = 'C' * 45
    log = AuditLog(
        user_id=99,
        action=max_action,
        resource_type=max_resource_type,
        resource_id=None,
        ip_address=max_ip
    )
    session.add(log)
    session.commit()
    saved = AuditLog.query.first()
    assert saved.action == max_action
    assert saved.resource_type == max_resource_type
    assert saved.ip_address == max_ip

def test_audit_log_json_fields_can_hold_complex_objects(session):
    """Edge case: before_state and after_state can store various JSON types."""
    log = AuditLog(
        user_id=1,
        action='UPDATE',
        before_state={'key': [1,2,3], 'nested': {'a': 'b'}},
        after_state=[1,2,3,4,5]
    )
    session.add(log)
    session.commit()
    saved = AuditLog.query.first()
    assert saved.before_state == {'key': [1,2,3], 'nested': {'a': 'b'}}
    assert saved.after_state == [1,2,3,4,5]