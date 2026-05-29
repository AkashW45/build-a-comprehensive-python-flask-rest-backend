def test_can_import_routes_package():
    """Verify the routes package exists and can be imported."""
    # The __init__.py is intentionally empty, serving as a package marker.
    # This test ensures no import-time errors occur.
    from employee_service.src.routes import __init__  # noqa: F401
    # If no exception is raised, import succeeded.