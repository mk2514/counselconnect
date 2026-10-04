# Infrastructure

Infrastructure-as-code and deployment configurations for CounselConnect.

## Current Setup

- **Local development**: Docker Compose (see `docker-compose.yml` at project root)
- **Database**: PostgreSQL 16
- **Cache**: Redis 7

## Production Infrastructure

Production infrastructure configurations will be added here when deployment targets are determined. This may include:

- Container orchestration (Kubernetes manifests, Helm charts)
- Cloud provider configurations
- CI/CD pipeline definitions
- Monitoring and alerting configurations
- Secret management
- Network policies

## Quick Start (Local Development)

```bash
# Start all services
docker compose up

# Start in detached mode
docker compose up -d

# Stop all services
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v
```
