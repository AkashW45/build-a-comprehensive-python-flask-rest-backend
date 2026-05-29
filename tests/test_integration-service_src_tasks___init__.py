import pytest

def test_import_tasks_module():
    """
    Happy path: Verify that the tasks package can be imported successfully.
    """
    try:
        from integration_service.src import tasks
    except ImportError as e:
        pytest.fail(f"Failed to import tasks module: {e}")
    assert tasks is not None

def test_tasks_is_package():
    """
    Edge case: Ensure that the tasks module is a Python package (has __path__).
    """
    from integration_service.src import tasks
    assert hasattr(tasks, '__path__'), "tasks should be a package"

def test_tasks_name_correct():
    """
    Edge case: Confirm the module's __name__ matches the expected dotted path.
    """
    from integration_service.src import tasks
    assert tasks.__name__ == 'integration_service.src.tasks', (
        f"Expected __name__ to be 'integration_service.src.tasks', got '{tasks.__name__}'"
    )

def test_tasks_no_exports():
    """
    Edge case: An empty __init__ should not accidentally expose any symbols via __all__.
    """
    from integration_service.src import tasks
    assert '__all__' not in dir(tasks), (
        "The tasks package should not define __all__ when empty"
    )

def test_import_nonexistent_attribute_raises_import_error():
    """
    Error path: Attempting to import a non‑existent attribute from the empty
    tasks package must raise an ImportError.
    """
    with pytest.raises(ImportError):
        from integration_service.src.tasks import NonExistentAttribute