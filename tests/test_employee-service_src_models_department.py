import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import db
from employee_service.src.models.department import Department

@pytest.fixture(scope="module")
def engine():
    """Create an in-memory SQLite engine for testing."""
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="module")
def tables(engine):
    """Create all tables from the db metadata."""
    db.metadata.create_all(engine)
    yield
    db.metadata.drop_all(engine)

@pytest.fixture
def session(engine, tables, monkeypatch):
    """Yield a session with transaction rollback after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    # Monkeypatch the db.session to use this test session
    monkeypatch.setattr(db, "session", session)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

def test_department_creation_happy_path(session):
    """Test creating a valid Department instance and persisting it."""
    dept = Department(name="Engineering", budget=150000.00, headcount_target=30)
    session.add(dept)
    session.commit()

    # Refresh from database
    session.refresh(dept)
    assert dept.id is not None, "Expected auto-generated ID"
    assert dept.name == "Engineering"
    assert dept.budget == 150000.00
    assert dept.headcount_target == 30
    # manager_id is optional, created_at should be set by server default
    assert dept.created_at is not None

def test_department_duplicate_name_raises_error(session):
    """Test that inserting a duplicate name violates the unique constraint."""
    dept1 = Department(name="HR")
    session.add(dept1)
    session.commit()

    dept2 = Department(name="HR")
    session.add(dept2)
    # The unique constraint will cause IntegrityError
    with pytest.raises(Exception):  # could be IntegrityError
        session.commit()
    # Rollback to keep session usable
    session.rollback()

def test_department_missing_name_raises_error(session):
    """Test that omitting name which is nullable=False raises an error."""
    dept = Department()  # no name
    session.add(dept)
    with pytest.raises(Exception):
        session.commit()
    session.rollback()

def test_department_budget_default(session):
    """Test that the budget field defaults to 0 when not provided."""
    dept = Department(name="DefaultBudget")
    session.add(dept)
    session.commit()
    session.refresh(dept)
    assert dept.budget == 0.00

def test_department_headcount_target_default(session):
    """Test that headcount_target defaults to 0 when not provided."""
    dept = Department(name="DefaultHeadcount")
    session.add(dept)
    session.commit()
    session.refresh(dept)
    assert dept.headcount_target == 0