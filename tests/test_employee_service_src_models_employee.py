import sys
from unittest.mock import MagicMock, patch

# Create mock for app.db to allow importing Employee without a real Flask app
mock_app = MagicMock()
mock_db = MagicMock()
mock_db.Model = type('Model', (object,), {})
mock_db.Column = MagicMock()
mock_db.String = MagicMock()
mock_db.Integer = MagicMock()
mock_db.Numeric = MagicMock()
mock_db.Date = MagicMock()
mock_db.DateTime = MagicMock()
mock_db.Boolean = MagicMock()
mock_db.ForeignKey = MagicMock()
mock_db.Index = MagicMock()
mock_db.func = MagicMock()
mock_app.db = mock_db

with patch.dict(sys.modules, {'app': mock_app}):
    from employee_service.src.models.employee import Employee


class TestEmployeeModel:
    def test_employee_to_dict_includes_required_fields(self):
        """Happy path: to_dict returns correct data for a fully populated employee."""
        emp = Employee(
            id=42,
            first_name='Alice',
            last_name='Johnson',
            email='alice@example.com',
            department_id=3,
            role='employee',
            active=True
        )
        result = emp.to_dict()
        expected = {
            'id': 42,
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'email': 'alice@example.com',
            'department_id': 3,
            'role': 'employee',
            'active': True
        }
        assert result == expected

    def test_employee_to_dict_excludes_optional_fields(self):
        """Edge case: to_dict ignores attributes not in its predefined list."""
        emp = Employee(
            id=1,
            first_name='Bob',
            last_name='Builder',
            email='bob@example.com',
            department_id=2,
            role='manager',
            active=False,
            phone='555-1234',
            salary=75000.50,
            location='NY'
        )
        result = emp.to_dict()
        assert 'phone' not in result
        assert 'salary' not in result
        assert 'location' not in result

    def test_minimal_employee_creation_to_dict(self):
        """Edge case: creating an employee with only required fields yields a valid dict."""
        emp = Employee(
            first_name='Carol',
            last_name='Danvers',
            email='carol@example.com',
            department_id=5,
            role='hr_manager'
        )
        result = emp.to_dict()
        assert result['first_name'] == 'Carol'
        assert result['last_name'] == 'Danvers'
        assert result['email'] == 'carol@example.com'
        assert result['department_id'] == 5
        assert result['role'] == 'hr_manager'
        # id is not set, so it should be None (or missing if not assigned)
        assert result['id'] is None
        # active not provided, should be None (no default applied in mocked model)
        assert result['active'] is None

    def test_full_text_search_indexes_are_defined(self):
        """Edge case: verify that the full‑text search indexes exist in __table_args__."""
        table_args = Employee.__table_args__
        # Expect two indexes: idx_employee_full_name and idx_employee_full_text
        assert len(table_args) == 2
        # Both should be instances of mock_db.Index (or at least not None)
        assert table_args[0] is not None
        assert table_args[1] is not None