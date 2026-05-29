# Compliance Service

Handles audit logging, GDPR data export and right-to-be-forgotten requests, and HIPAA-compliant medical leave records.

## Endpoints

- `GET /compliance/audit-logs` - Paginated audit log list
- `POST /compliance/gdpr/export` - Request data export
- `POST /compliance/gdpr/forget` - Request data deletion
- `GET/POST /compliance/medical-leaves` - List or create medical leave records

## Environment Variables

- `DATABASE_URL`
- `OTEL_EXPORTER_OTLP_ENDPOINT`

## Running

bash
pip install -r requirements.txt
python app.py

