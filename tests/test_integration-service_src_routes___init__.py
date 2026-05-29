import pytest


def test_imports_without_error():
    """
    Happy path: the routes package can be imported without any exception.
    """
    try:
        import routes
    except Exception as e:
        pytest.fail(f"Failed to import 'routes' package: {e}")


def test_routes_is_a_package():
    """
    Edge case: the imported module has the __path__ attribute,
    confirming it is a Python package and not a plain module.
    """
    import routes
    assert hasattr(routes, "__path__"), "'routes' should be a package (with __path__)"


def test_import_nonexistent_submodule_raises():
    """
    Error path: importing a submodule that does not exist
    must raise a ModuleNotFoundError (subclass of ImportError).
    """
    with pytest.raises(ImportError):
        from routes import definitely_not_a_valid_submodule_123xyz