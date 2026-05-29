# Employee Service

Manages employee data including CRUD, history, transfers, promotions, and full-text search.

## Endpoints

- `GET /employees` - List employees (paginated, filterable)
- `POST /employees` - Create employee
- `GET /employees/{id}` - Get employee details
- `PUT /employees/{id}` - Update employee
- `PATCH /employees/{id}/status` - Update active status
- `DELETE /employees/{id}` - Delete employee
- `GET /employees/search?q=...` - Full-text search

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `OTEL_EXPORTER_OTLP_ENDPOINT`

## Running

bash
pip install -r requirements.txt
export DATABASE_URL=postgresql://...
python app.py

