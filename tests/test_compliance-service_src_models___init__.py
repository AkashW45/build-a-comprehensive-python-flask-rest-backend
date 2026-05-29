import pytest
from models import AuditLog, GDPRRequest, MedicalLeave


def test_audit_log_imported():
    """Happy path: AuditLog class is importable from the models package."""
    assert AuditLog is not None
    assert isinstance(AuditLog, type)


def test_gdpr_request_imported():
    """Happy path: GDPRRequest class is importable."""
    assert GDPRRequest is not None
    assert isinstance(GDPRRequest, type)


def test_medical_leave_imported():
    """Happy path: MedicalLeave class is importable."""
    assert MedicalLeave is not None
    assert isinstance(MedicalLeave, type)


def test_importing_nonexistent_class_raises_import_error():
    """
    Error path: Attempting to import a class that does not exist in this package
    raises ImportError.
    """
    with pytest.raises(ImportError):
        from models import NonExistentClass  # noqa