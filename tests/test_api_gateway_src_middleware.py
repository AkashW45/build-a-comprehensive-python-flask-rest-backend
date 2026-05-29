import pytest
from unittest.mock import patch
from api_gateway_src.middleware import role_required

def test_role_required_happy_path():
    """Happy path: user has the required role."""
    with patch('api_gateway_src.middleware.verify_jwt_in_request') as mock_verify, \
         patch('api_gateway_src.middleware.get_jwt_claims', return_value={'role': 'admin'}):
        @role_required('admin')
        def my_view():
            return 'success', 200

        result = my_view()
        mock_verify.assert_called_once()
        assert result == ('success', 200)

def test_role_required_insufficient_permissions():
    """Error path: user role does not match required role."""
    with patch('api_gateway_src.middleware.verify_jwt_in_request'), \
         patch('api_gateway_src.middleware.get_jwt_claims', return_value={'role': 'employee'}):
        @role_required('admin')
        def my_view():
            return 'success', 200

        response = my_view()
        assert response[1] == 403
        assert response[0].json['msg'] == 'Insufficient permissions'

def test_role_required_missing_role_key():
    """Edge case: claims do not contain 'role' key."""
    with patch('api_gateway_src.middleware.verify_jwt_in_request'), \
         patch('api_gateway_src.middleware.get_jwt_claims', return_value={'other': 'data'}):
        @role_required('admin')
        def my_view():
            return 'success', 200

        response = my_view()
        assert response[1] == 403
        assert response[0].json['msg'] == 'Insufficient permissions'

def test_role_required_missing_jwt():
    """Error path: verify_jwt_in_request raises an exception (missing/invalid token)."""
    from flask_jwt_extended import NoAuthorizationError
    with patch('api_gateway_src.middleware.verify_jwt_in_request', side_effect=NoAuthorizationError('Missing token')), \
         patch('api_gateway_src.middleware.get_jwt_claims') as mock_claims:
        @role_required('admin')
        def my_view():
            return 'success', 200

        with pytest.raises(NoAuthorizationError):
            my_view()
        mock_claims.assert_not_called()