# Repository Instructions

## Current State

- The inventory API is implemented. `run.py` creates the app; `app/__init__.py` wires extensions and blueprints.

## Intended Application

- Build a versioned Flask REST API for inventory management under `/api/v1`.
- Use Python 3.12, Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Smorest/Marshmallow, pytest, SQLite locally, Gunicorn, and Docker.
- Keep the application modular: an app factory plus separate `models`, `schemas`, and `api` packages. `run.py` is the local entrypoint.
- Scope is categories, products, stock adjustments, product querying/pagination, consistent JSON errors, OpenAPI/Swagger docs, migrations, tests, and Docker. Authentication is intentionally out of scope.

## Domain Invariants

- Category names and product SKUs are unique.
- Product price and stock quantity cannot be negative.
- Change inventory only through `POST /api/v1/products/{id}/stock`; ordinary product updates must not alter quantity.
- Every successful stock adjustment creates an immutable `StockMovement` in the same database transaction.
- Reject zero-value stock adjustments and adjustments that would make stock negative.
- Do not delete a category that is referenced by products.
- Return movement history newest first.

## Verification Expectations

- Use an isolated SQLite database for pytest; tests must not read or modify the development database.
- Cover success, schema validation, duplicate conflicts, missing resources, unsafe category deletion, and insufficient stock.
- Before calling the project complete, verify a clean migration, the full pytest suite, Docker image creation, and category/product/stock flows through the running API.

## Verified Commands

- Install dependencies: `python -m pip install -r requirements.txt`.
- Apply migrations: `python -m flask --app run:app db upgrade`.
- Run locally: `python run.py` (port 5000); Swagger UI is `/docs`.
- Run all tests: `pytest -q`; run one with `pytest tests/test_stock.py::test_stock_adjustments_create_newest_first_history -q`.
- Build/run the container: `docker compose up --build` (port 8000); startup applies migrations before Gunicorn.
- Tests use temporary SQLite files from `tests/conftest.py`; keep this isolation when adding fixtures.
- CI development tools install from `requirements-dev.txt`; runtime images install only `requirements.txt`.
- Migration drift validation uses `python -m flask --app run:app db check` after `db upgrade`.
- CI workflow is `.github/workflows/ci-cd.yml`; Docker Hub needs `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` repository secrets.
- Docker publication is restricted to pushes on `main`, `v*` tags, or a manual dispatch with `publish=true`; pull requests never publish.

## API Shape

- `GET /api/v1/products` returns `{items, pagination}`; query parsing is defined in `ProductQuerySchema`.
- Product prices serialize as decimal strings, not JSON floats.
- Use Flask-Smorest's `abort`, not Flask's, when supplying the custom application error `code`.
