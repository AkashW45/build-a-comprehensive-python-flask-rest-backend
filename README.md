# Enterprise HR Management System

Microservices-based Flask REST API for HR operations, compliance, and integrations.

## Architecture

- **API Gateway**: Authentication, rate limiting, routing
- **Auth Service**: User management, JWT, MFA, SAML
- **Employee Service**: Employee CRUD, search, history
- **Department Service**: Department CRUD, budget, headcount
- **Payroll Service**: Payroll runs, pay stubs, tax calculations
- **Leave Service**: Leave requests, balances, policies
- **Performance Service**: Performance reviews, goals, feedback
- **Recruitment Service**: Job postings, applications, interviews, offers
- **Integration Service**: Async Slack, SendGrid, S3, Stripe, ADP via Celery
- **Compliance Service**: Audit logs, GDPR, HIPAA medical leaves
- **Databases**: PostgreSQL primary + read-replica, Redis
- **Observability**: Prometheus, Grafana, OpenTelemetry
- **Deployment**: Kubernetes with blue-green updates

## Getting Started

1. Set up infrastructure using docker-compose: `cd infrastructure && docker-compose up -d`
2. Each service can be run individually for development.
3. See each service's README for specific instructions.

## Testing

Each service includes pytest test suites. For integration tests, use Testcontainers (see `docker-compose-test.yml`).

## License

Proprietary
