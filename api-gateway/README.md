# API Gateway

Serves as the single entry point for the HR management system. Handles authentication, rate limiting, and routes requests to internal microservices.

## Endpoints

- `POST /api/v1/auth/login` - Authenticate and get JWT tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/mfa/verify` - Verify MFA code
- All other `/api/v1/*` routes proxy to respective microservices

## Configuration

Environment variables:
- `JWT_SECRET_KEY`
- `REDIS_URL`
- `OTEL_EXPORTER_OTLP_ENDPOINT`
- Microservice URLs: `EMPLOYEE_SERVICE_URL`, etc.

## Running

bash
pip install -r requirements.txt
python app.py


## Docker

bash
docker build -t api-gateway .
docker run -p 5000:5000 api-gateway

