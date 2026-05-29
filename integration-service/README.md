# Integration Service

Handles asynchronous external integrations via Celery tasks.

## Endpoints

- `POST /integrations/slack/notify` - Trigger Slack notification
- `POST /integrations/email/send` - Send email
- `POST /integrations/s3/upload` - Upload document to S3
- `POST /integrations/stripe/enroll` - Process Stripe benefits enrollment
- `POST /integrations/adp/sync` - Sync payroll with ADP

## Environment Variables

- `SLACK_BOT_TOKEN`
- `SENDGRID_API_KEY`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`
- `STRIPE_SECRET_KEY`
- `ADP_API_URL`
- `CELERY_BROKER_URL`
- `OTEL_EXPORTER_OTLP_ENDPOINT`

## Running

Start Celery worker:
bash
celery -A app.celery_app worker --loglevel=info


Start Flask app:
bash
python app.py

