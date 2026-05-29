# Auth Service

Handles user authentication, JWT token management, MFA, SSO, password policies, and RBAC enforcement.

## Endpoints

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login (returns JWT tokens)
- `POST /api/v1/auth/mfa/setup` - Setup TOTP MFA
- `POST /api/v1/auth/mfa/verify` - Verify MFA code
- `POST /api/v1/auth/sso/login` - SAML SSO login (placeholder)

## Environment Variables

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `OTEL_EXPORTER_OTLP_ENDPOINT`

## Running

bash
pip install -r requirements.txt
python app.py

