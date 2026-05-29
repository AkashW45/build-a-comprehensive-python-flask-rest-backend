import pytest

def test_package_importable():
    """Happy path: The integration_service package can be imported."""
    import integration_service
    assert hasattr(integration_service, '__path__'), "Package must have a __path__ attribute"

def test_package_has_no_unexpected_symbols():
    """Edge case: An empty __init__.py should not define extra symbols."""
    import integration_service
    default_attrs = {'__name__', '__doc__', '__package__', '__loader__', '__spec__', '__path__', '__builtins__', '__file__', '__cached__'}
    custom_attrs = set(dir(integration_service)) - default_attrs
    assert custom_attrs == set(), f"Unexpected symbols found: {custom_attrs}"

def test_import_nonexistent_submodule_raises():
    """Error path: Importing a non-existent submodule raises ImportError."""
    with pytest.raises(ImportError):
        from integration_service import nonexistent_submodule