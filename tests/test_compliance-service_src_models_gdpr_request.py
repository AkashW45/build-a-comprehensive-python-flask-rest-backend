import pytest
from flask import Flask
from app import db
from compliance_service.src.models.gdpr_request import GDPRRequest
from datetime import datetime, timedelta

@pytest.fixture(scope='module')
def test_app():
    """Create a test Flask app with in-memory SQLite database."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture(scope='function')
def session(test_app):
    """Provide a database session within an app context."""
    with test_app.app_context():
        yield db.session
        db.session.rollback()

def test_gdpr_request_creation_happy_path(session):
    """Happy path: create and retrieve a GDPR request with all fields."""
    req = GDPRRequest(
        user_id=42,
        request_type='export',
        status='pending',
        data_payload={'fields': ['name', 'email']}
    )
    session.add(req)
    session.commit()

    saved = session.query(GDPRRequest).filter_by(id=req.id).first()
    assert saved is not None
    assert saved.user_id == 42
    assert saved.request_type == 'export'
    assert saved.status == 'pending'
    assert isinstance(saved.created_at, datetime)
    assert saved.completed_at is None
    assert saved.data_payload == {'fields': ['name', 'email']}

def test_gdpr_request_default_status(session):
    """Default status must be 'pending'."""
    req = GDPRRequest(user_id=1)
    session.add(req)
    session.commit()

    saved = session.query(GDPRRequest).filter_by(id=req.id).first()
    assert saved.status == 'pending'

def test_gdpr_request_auto_created_at(session):
    """created_at must be set automatically to current UTC time."""
    before = datetime.utcnow()
    req = GDPRRequest(user_id=5)
    session.add(req)
    session.commit()
    after = datetime.utcnow()

    saved = session.query(GDPRRequest).filter_by(id=req.id).first()
    assert before <= saved.created_at <= after

def test_gdpr_request_nullable_fields(session):
    """completed_at and data_payload can be NULL."""
    req = GDPRRequest(user_id=7)
    session.add(req)
    session.commit()

    saved = session.query(GDPRRequest).filter_by(id=req.id).first()
    assert saved.completed_at is None
    assert saved.data_payload is None

def test_gdpr_request_missing_user_id_raises_error(session):
    """Model must reject missing user_id because nullable=False."""
    req = GDPRRequest()  # no user_id
    session.add(req)
    with pytest.raises(Exception) as excinfo:
        session.commit()
    # SQLite may raise IntegrityError or SQLAlchemy may detect before.
    assert excinfo.type is not None

def test_gdpr_request_id_autoincrement(session):
    """Verify that id is auto-incremented."""
    req1 = GDPRRequest(user_id=100)
    req2 = GDPRRequest(user_id=101)
    session.add_all([req1, req2])
    session.commit()

    assert req1.id is not None
    assert req2.id is not None
    assert req2.id == req1.id + 1

def test_gdpr_request_json_data_payload_export(session):
    """Ensure JSON column correctly stores export payload."""
    payload = {'employee_data': ['id', 'department'], 'format': 'csv'}
    req = GDPRRequest(
        user_id=200,
        request_type='export',
        data_payload=payload
    )
    session.add(req)
    session.commit()

    saved = session.query(GDPRRequest).filter_by(id=req.id).first()
    assert saved.data_payload == payload
    assert saved.request_type == 'export'