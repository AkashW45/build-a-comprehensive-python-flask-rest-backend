import pytest
from auth_service.src.policy import validate_password

def test_validate_password_valid_happy_path():
    """Password meets all requirements"""
    assert validate_password("Valid1$123") is True

def test_validate_password_too_short_error():
    """Password shorter than 8 characters"""
    assert validate_password("A1!a") is False

def test_validate_password_missing_uppercase_error():
    """Password missing uppercase letter"""
    assert validate_password("nouppercase1!") is False

def test_validate_password_missing_lowercase_error():
    """Password missing lowercase letter"""
    assert validate_password("NOLOWERCASE1!") is False

def test_validate_password_missing_digit_error():
    """Password missing digit"""
    assert validate_password("NoDigitHere!") is False

def test_validate_password_missing_special_char_error():
    """Password missing special character"""
    assert validate_password("NoSpecial1") is False