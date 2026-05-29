from flask import Flask
from celery import Celery
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import os

def create_celery_app():
    celery_app = Celery(
        'integration',
        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    )
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
    )
    return celery_app

celery_app = create_celery_app()

def create_flask_app():
    app = Flask(__name__)
    
    metrics = PrometheusMetrics(app, group_by='endpoint')
    
    trace.set_tracer_provider(TracerProvider())
    otlp_exporter = OTLPSpanExporter(endpoint=os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4318/v1/traces'))
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    FlaskInstrumentor().instrument_app(app)
    
    from src.routes.integration_routes import integration_bp
    app.register_blueprint(integration_bp, url_prefix='/integrations')
    
    @app.route('/health')
    def health():
        return {'status': 'ok'}
    
    return app

app = create_flask_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5020)
