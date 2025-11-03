# Public Water System Dashboard

This project displays parameters of the public water system for your local town using a modern web stack:

- **NGINX**: Reverse proxy for routing requests
- **PostgreSQL**: Database for storing water system parameters
- **FastAPI**: Python backend serving API endpoints
- **Dash**: Python frontend for interactive dashboards

## Project Structure

- `nginx/` — NGINX config and Dockerfile
- `db/` — PostgreSQL initialization scripts
- `backend/` — FastAPI backend app
- `frontend/` — Dash frontend app
- `docker-compose.yml` — Orchestrates all services

## Usage

1. Build and start all services:
   ```sh
   docker-compose up --build
   ```
2. Access the dashboard at [http://localhost](http://localhost)

## Development Setup

For local development, use the `docker-compose.dev.yml` file to override specific parameters like ports and environment variables. Run the following command:

```sh
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Development Overrides
- **Database**: Runs on port `5433` with credentials `devuser/devpass` and database `aigualba_db`.
- **Backend**: Accessible on port `8001`.
- **Frontend**: Accessible on port `8051`.
- **NGINX**: Accessible on port `8088`.

This setup allows you to test changes locally without affecting the production configuration.

## Customization
- Add more parameters to `db/init.sql`.
- Extend backend API in `backend/main.py`.
- Customize dashboard in `frontend/app.py`.

---

Replace placeholder code and configuration as needed for your specific requirements.
