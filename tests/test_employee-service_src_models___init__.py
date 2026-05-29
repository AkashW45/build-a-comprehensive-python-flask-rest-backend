import pytest
from employee_service.src.models import Employee, Department

def test_employee_is_imported():
    """Verify that Employee is importable and is a class."""
    assert Employee is not None
    assert isinstance(Employee, type)

def test_department_is_imported():
    """Verify that Department is importable and is a class."""
    assert Department is not None
    assert isinstance(Department, type)