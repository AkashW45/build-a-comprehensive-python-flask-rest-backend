from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import redis
import os

def create_app():
    app = Flask(__name__)
    api = Api(app)
    
    # Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 15 * 60  # 15 minutes
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 30 * 24 * 3600  # 30 days
    
    # JWT
    jwt = JWTManager(app)
    
    # Rate Limiter with Redis
    redis_client = redis.Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Prometheus metrics
    metrics = PrometheusMetrics(app, group_by='endpoint')
    
    # OpenTelemetry tracing
    trace.set_tracer_provider(TracerProvider())
    otlp_exporter = OTLPSpanExporter(endpoint=os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4318/v1/traces'))
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    FlaskInstrumentor().instrument_app(app)
    
    # Health check
    @app.route('/health')
    def health():
        return {'status': 'ok'}
    
    # Register blueprints or routes
    from src.routes.auth_routes import auth_bp
    from src.routes.proxy_routes import proxy_bp
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(proxy_bp, url_prefix='/api/v1')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, threaded=True)
