import pytest

def test_routes_package_imports_without_error():
    """Test that the routes __init__.py can be imported."""
    try:
        import compliance_service.src.routes as routes
    except ImportError as e:
        pytest.fail(f"Failed to import routes package: {e}")

def test_routes_package_is_a_module():
    """Test that the imported routes object is a valid module."""
    import compliance_service.src.routes as routes
    from types import ModuleType
    assert isinstance(routes, ModuleType), "routes is not a module"

def test_routes_package_has_no_side_effects():
    """Test that the empty __init__.py does not create unexpected global attributes (edge case)."""
    import compliance_service.src.routes as routes
    # The __init__.py is empty, so no extra attributes should exist besides standard module attributes
    standard_attrs = {'__name__', '__doc__', '__package__', '__loader__', '__spec__', '__path__', '__file__', '__cached__', '__builtins__'}
    extra_attrs = set(dir(routes)) - standard_attrs
    # Allow attributes that are common in a package (e.g., sub-modules if already imported)
    # Since the file is empty, the only possible extra attrs are those from import side effects.
    assert extra_attrs == set(), f"Unexpected attributes found: {extra_attrs}"

def test_accessing_nonexistent_attribute_raises_attribute_error():
    """Error path: accessing a non-existent attribute on the routes module raises AttributeError."""
    import compliance_service.src.routes as routes
    with pytest.raises(AttributeError):
        _ = routes.non_existent_attribute