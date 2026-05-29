import pytest
from flask import Flask
from sqlalchemy.exc import IntegrityError

from app import db
from models.mfa import MFA


@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)

    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def test_create_mfa_defaults(app):
    """Happy path: create an MFA record and verify defaults."""
    with app.app_context():
        mfa = MFA(user_id=1, secret='testsecret')
        db.session.add(mfa)
        db.session.commit()

        saved = db.session.get(MFA, mfa.id)
        assert saved is not None
        assert saved.user_id == 1
        assert saved.secret == 'testsecret'
        assert saved.method == 'totp'
        assert saved.enabled is False


def test_mfa_missing_user_id(app):
    """Error path: omit required user_id raises IntegrityError."""
    with app.app_context():
        mfa = MFA(secret='nosecret')  # user_id missing, it's required
        db.session.add(mfa)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_mfa_missing_secret(app):
    """Error path: omit required secret raises IntegrityError."""
    with app.app_context():
        mfa = MFA(user_id=1)  # secret missing
        db.session.add(mfa)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_mfa_method_override(app):
    """Edge case: set a custom method and verify it persists."""
    with app.app_context():
        mfa = MFA(user_id=2, secret='anothersecret', method='sms')
        db.session.add(mfa)
        db.session.commit()

        saved = db.session.get(MFA, mfa.id)
        assert saved.method == 'sms'
        # default for enabled still False
        assert saved.enabled is False