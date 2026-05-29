import sys
import pytest

def test_src_module_imports_successfully():
    """Verify that the src package (from employee-service/src/__init__.py) can be imported."""
    # The module is 'src' because the __init__.py resides directly in the src directory.
    import src
    assert src is not None
    assert isinstance(src, type(sys)) or hasattr(src, '__path__')

def test_src_module_has_name():
    """Check that the module's __name__ is correct."""
    import src
    assert src.__name__ == 'src'

def test_src_module_reimport_idempotent():
    """Ensure that re-importing the module does not cause side effects (e.g., missing attributes)."""
    import src
    import importlib
    # Reloading should not raise and the module object should remain consistent
    src2 = importlib.reload(src)
    assert src2 is src  # In CPython, reloading returns the same module object
    assert hasattr(src2, '__name__')

def test_src_module_unknown_attribute_raises_error():
    """Accessing an arbitrary non-existent attribute should raise AttributeError."""
    import src
    with pytest.raises(AttributeError):
        _ = src.NON_EXISTENT_ATTRIBUTE_XYZ