import pytest
from unittest.mock import patch, MagicMock
import os
import redis
from api_gateway.app import create_app


@patch('api_gateway.app.redis.Redis.from_url')
@patch('api_gateway.app.PrometheusMetrics')
@patch('api_gateway.app.FlaskInstrumentor')
@patch('api_gateway.app.OTLPSpanExporter')
@patch('api_gateway.app.trace')
def test_create_app_success(mock_trace, mock_otlp_exporter, mock_instrumentor_cls, mock_prometheus, mock_redis_from_url):
    """Happy path: create_app returns Flask app with health endpoint, JWT, limiter, and registered blueprints."""
    # Setup mocks
    mock_redis_client = MagicMock()
    mock_redis_from_url.return_value = mock_redis_client
    mock_instrumentor = MagicMock()
    mock_instrumentor_cls.return_value = mock_instrumentor

    app = create_app()

    # Basic assertions
    assert app is not None
    assert isinstance(app, app.__class__)  # Flask instance

    # Health endpoint
    with app.test_client() as client:
        resp = client.get('/health')
        assert resp.status_code == 200
        assert resp.json == {'status': 'ok'}

    # Extensions
    assert 'jwt' in app.extensions
    assert 'limiter' in app.extensions

    # Blueprints
    assert 'auth_bp' in app.blueprints
    assert 'proxy_bp' in app.blueprints

    # Instrumentation called
    mock_instrumentor_cls.assert_called_once()
    mock_instrumentor.instrument_app.assert_called_once_with(app)


@patch('api_gateway.app.redis.Redis.from_url')
def test_create_app_redis_failure(mock_redis_from_url):
    """Error path: Redis unavailable raises ConnectionError when creating the app."""
    mock_redis_from_url.side_effect = redis.exceptions.ConnectionError("Redis down")

    with pytest.raises(redis.exceptions.ConnectionError):
        create_app()


@patch('api_gateway.app.redis.Redis.from_url')
@patch('api_gateway.app.PrometheusMetrics')
@patch('api_gateway.app.FlaskInstrumentor')
@patch('api_gateway.app.OTLPSpanExporter')
@patch('api_gateway.app.trace')
def test_rate_limiter_default_limits(mock_trace, mock_otlp, mock_instr_cls, mock_prom, mock_redis_fu):
    """Edge case: verify Flask-Limiter default limits are set correctly."""
    mock_redis_fu.return_value = MagicMock()
    app = create_app()

    limiter = app.extensions['limiter']
    assert hasattr(limiter, 'default_limits')
    default_limits = limiter.default_limits  # list of strings
    assert any('200 per day' in rule for rule in default_limits)
    assert any('50 per hour' in rule for rule in default_limits)


@patch('api_gateway.app.redis.Redis.from_url')
@patch('api_gateway.app.PrometheusMetrics')
@patch('api_gateway.app.FlaskInstrumentor')
@patch('api_gateway.app.OTLPSpanExporter')
@patch('api_gateway.app.trace')
def test_blueprints_registered(mock_trace, mock_otlp, mock_instr, mock_prom, mock_redis):
    """Edge case: ensure auth and proxy blueprints are fully registered after app creation."""
    mock_redis.return_value = MagicMock()
    app = create_app()

    assert 'auth_bp' in app.blueprints
    assert 'proxy_bp' in app.blueprints

    # Optionally check URL prefixes
    assert any('/api/v1/auth' in str(rule) for rule in app.url_map.iter_rules())
    assert any('/api/v1' in str(rule) for rule in app.url_map.iter_rules())


@patch('api_gateway.app.redis.Redis.from_url')
@patch('api_gateway.app.PrometheusMetrics')
@patch('api_gateway.app.FlaskInstrumentor')
@patch('api_gateway.app.OTLPSpanExporter')
@patch('api_gateway.app.trace')
def test_opentelemetry_setup(mock_trace, mock_otlp_exporter_cls, mock_instrumentor_cls, mock_prom, mock_redis):
    """Edge case: verify OpenTelemetry tracer provider, exporter, and instrumentation are correctly configured."""
    mock_redis.return_value = MagicMock()
    mock_instrumentor = MagicMock()
    mock_instrumentor_cls.return_value = mock_instrumentor

    app = create_app()

    # Tracer provider set
    mock_trace.set_tracer_provider.assert_called_once()

    # OTLP exporter instantiated with endpoint from env (or default)
    expected_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4318/v1/traces')
    mock_otlp_exporter_cls.assert_called_once_with(endpoint=expected_endpoint)

    # Span processor added to tracer provider
    provider = mock_trace.get_tracer_provider.return_value
    provider.add_span_processor.assert_called_once()

    # Flask instrumentation applied
    mock_instrumentor.instrument_app.assert_called_once_with(app)