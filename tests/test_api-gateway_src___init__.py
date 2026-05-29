import pytest
import importlib

def test_import_package():
    """Test that the package can be imported without errors."""
    try:
        pkg = importlib.import_module('api_gateway_src')
        assert pkg is not None, "Imported package should not be None"
    except Exception as e:
        pytest.fail(f"Failed to import api_gateway_src package: {e}")

def test_package_attributes():
    """Test that the package has expected module-level attributes."""
    import api_gateway_src
    # Basic check that it is a module/package
    assert hasattr(api_gateway_src, '__name__'), "Package should have __name__"
    assert api_gateway_src.__name__ == 'api_gateway_src', "Package __name__ should match the import name"
    # __package__ may be empty string for top-level packages or 'api_gateway_src'
    assert hasattr(api_gateway_src, '__package__'), "Package should have __package__"