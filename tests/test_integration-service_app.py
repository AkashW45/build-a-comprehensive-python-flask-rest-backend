import pytest
from app import create_celery_app, create_flask_app

class TestCeleryApp:
    def test_celery_defaults(self):
        celery = create_celery_app()
        assert celery is not None
        assert celery.main == 'integration'
        assert celery.conf.task_serializer == 'json'
        assert celery.conf.accept_content == ['json']
        assert celery.conf.result_serializer == 'json'
        assert celery.conf.timezone == 'UTC'
        assert celery.conf.enable_utc is True
        assert celery.conf.task_track_started is True
        assert celery.conf.task_time_limit == 30 * 60

@pytest.fixture
def client():
    app = create_flask_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestFlaskApp:
    def test_health_success(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json == {'status': 'ok'}

    def test_health_method_not_allowed(self, client):
        response = client.post('/health')
        assert response.status_code == 405

    def test_blueprint_registered(self, client):
        app = create_flask_app()
        assert 'integration_bp' in app.blueprints
        # Blueprint prefix should be '/integrations'
        # A request to a non‑existent route inside the blueprint should return 404
        response = client.get('/integrations/nonexistent')
        assert response.status_code == 404