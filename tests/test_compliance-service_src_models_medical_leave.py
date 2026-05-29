import sys
import pytest
from datetime import date, datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

# ----------------------------------------------------------------------
# Setup a fake app module so that the real MedicalLeave model, which
# does `from app import db`, can be imported inside this test suite.
# ----------------------------------------------------------------------
_fake_app = Flask(__name__)
_fake_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
_fake_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
_fake_db = SQLAlchemy(_fake_app)

_fake_app_module = type(sys)('app')
_fake_app_module.app = _fake_app
_fake_app_module.db = _fake_db
sys.modules['app'] = _fake_app_module

# Now import the model — this will pick up our fake_db
from src.models.medical_leave import MedicalLeave  # noqa: E402


@pytest.fixture(scope='function')
def db_session():
    """Provide a fresh in‑memory SQLite database pre‑populated with the
    MedicalLeave table."""
    with _fake_app.app_context():
        _fake_db.create_all()
    yield _fake_db.session
    with _fake_app.app_context():
        _fake_db.session.remove()
        _fake_db.drop_all()


class TestMedicalLeaveModel:
    """Tests for the MedicalLeave model with HIPAA‑relevant fields."""

    def test_create_medical_leave_happy_path(self, db_session):
        """Happy path: a fully populated medical leave record can be persisted."""
        leave = MedicalLeave(
            employee_id=42,
            reason="Surgery recovery",
            start_date=date(2025, 1, 15),
            end_date=date(2025, 2, 28),
            documents={"s3_key": "bucket/doc1.pdf"}
        )
        db_session.add(leave)
        db_session.commit()

        saved = db_session.query(MedicalLeave).filter_by(employee_id=42).one()
        assert saved.id is not None
        assert saved.employee_id == 42
        assert saved.reason == "Surgery recovery"
        assert saved.start_date == date(2025, 1, 15)
        assert saved.end_date == date(2025, 2, 28)
        assert saved.documents == {"s3_key": "bucket/doc1.pdf"}
        assert isinstance(saved.created_at, datetime)

    def test_create_with_only_required_fields(self, db_session):
        """Edge case: only required fields (employee_id, start_date) are
        supplied; optional fields default to None."""
        leave = MedicalLeave(
            employee_id=7,
            start_date=date(2025, 3, 1)
        )
        db_session.add(leave)
        db_session.commit()

        saved = db_session.query(MedicalLeave).filter_by(employee_id=7).one()
        assert saved.employee_id == 7
        assert saved.start_date == date(2025, 3, 1)
        assert saved.reason is None       # HIPAA – only when necessary
        assert saved.end_date is None
        assert saved.documents is None

    def test_missing_employee_id_raises_integrity_error(self, db_session):
        """Error path: employee_id is not nullable → IntegrityError."""
        leave = MedicalLeave(
            start_date=date(2025, 4, 10)
        )
        db_session.add(leave)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_missing_start_date_raises_integrity_error(self, db_session):
        """Error path: start_date is not nullable → IntegrityError."""
        leave = MedicalLeave(employee_id=99)
        db_session.add(leave)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_reason_can_be_none(self, db_session):
        """HIPAA consideration: reason is optional and can be NULL."""
        leave = MedicalLeave(
            employee_id=123,
            start_date=date(2025, 5, 1),
            reason=None        # explicitly None
        )
        db_session.add(leave)
        db_session.commit()

        saved = db_session.query(MedicalLeave).filter_by(employee_id=123).one()
        assert saved.reason is None

    def test_index_on_employee_id_exists(self, db_session):
        """Ensure the database index for employee_id lookups is present."""
        table = MedicalLeave.__table__
        index_names = {idx.name for idx in table.indexes}
        assert 'idx_medical_employee' in index_names