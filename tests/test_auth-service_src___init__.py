import importlib
import sys
from pathlib import Path
import pytest

def test_import_package():
    """Test that the auth-service.src package can be imported without errors."""
    # The directory name contains a dash, so standard import is not possible.
    # We load the module via file location.
    init_path = Path(__file__).resolve().parent.parent / "auth-service" / "src" / "__init__.py"
    if not init_path.exists():
        pytest.skip("Package file not found")
    spec = importlib.util.spec_from_file_location("auth_service.src", str(init_path))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        pytest.fail(f"Import failed: {e}")

def test_package_has_no_unexpected_exports():
    """Ensure the empty __init__.py does not accidentally define public symbols."""
    init_path = Path(__file__).resolve().parent.parent / "auth-service" / "src" / "__init__.py"
    if not init_path.exists():
        pytest.skip("Package file not found")
    spec = importlib.util.spec_from_file_location("auth_service.src", str(init_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Only dunder attributes and standard module members should be present.
    unexpected = [attr for attr in dir(module) if not attr.startswith('__')]
    assert not unexpected, f"Found unexpected public attributes: {unexpected}"

def test_import_dunder_all_behavior():
    """Check that no __all__ is accidentally defined."""
    init_path = Path(__file__).resolve().parent.parent / "auth-service" / "src" / "__init__.py"
    if not init_path.exists():
        pytest.skip("Package file not found")
    spec = importlib.util.spec_from_file_location("auth_service.src", str(init_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert not hasattr(module, '__all__') or module.__all__ is None, \
        "__all__ should not be defined in an empty package init"