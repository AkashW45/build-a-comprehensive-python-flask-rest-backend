import pytest
from auth_service.src.models import User, MFA


def test_user_imported():
    """Happy path: User symbol is accessible after import."""
    assert User is not None


def test_mfa_imported():
    """Happy path: MFA symbol is accessible after import."""
    assert MFA is not None


def test_user_is_class():
    """Edge case: User is a class (type)."""
    assert isinstance(User, type)


def test_mfa_is_class():
    """Edge case: MFA is a class (type)."""
    assert isinstance(MFA, type)


def test_no_extra_public_symbols():
    """Edge case: Only User and MFA are exposed."""
    import auth_service.src.models as models
    expected = {'User', 'MFA'}
    # filter out dunder and private names
    public = {name for name in dir(models) if not name.startswith('_')}
    assert public == expected


def test_user_and_mfa_are_different():
    """Edge case: User and MFA are distinct classes."""
    assert User is not MFA