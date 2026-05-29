import pytest

def test_import_routes_package():
    """Test that the routes package can be imported without error."""
    try:
        import routes
    except ImportError as e:
        pytest.fail(f"Failed to import routes package: {e}")

def test_routes_init_no_unexpected_side_effects():
    """Test that the __init__.py does not define any unexpected global symbols."""
    import routes
    assert not hasattr(routes, '__all__') or routes.__all__ == [], \
        "routes package should not expose any symbols via __all__"