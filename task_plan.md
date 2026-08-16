# Inventory API Implementation Plan

## Goal

Build and verify a versioned Flask inventory REST API matching `AGENTS.md`.

## Architecture

Use a Flask application factory with extension objects initialized separately. SQLAlchemy models own persistence constraints, Marshmallow schemas own request/response validation, and Flask-Smorest blueprints expose categories, products, stock adjustments, movement history, and OpenAPI documentation under `/api/v1`.

## Phases

### Phase 1: Plan and foundation
**Status:** complete

- [x] Confirm scope and invariants from `AGENTS.md`.
- [x] Add Python dependency/configuration files and application factory.
- [x] Add isolated application test fixture and health test.

### Phase 2: Categories
**Status:** complete

- [x] Add category model and request/response schemas.
- [x] Add category CRUD with duplicate and referenced-delete conflicts.
- [x] Test success, validation, conflict, and missing-resource behavior.

### Phase 3: Products and querying
**Status:** complete

- [x] Add product model and create/update/output schemas.
- [x] Add product CRUD without quantity mutation through ordinary updates.
- [x] Add search, category/price/low-stock filters, sorting, and pagination.
- [x] Test validation, duplicates, missing categories, and query behavior.

### Phase 4: Stock ledger
**Status:** complete

- [x] Add immutable stock movement model and schemas.
- [x] Add transactional non-zero stock adjustments with negative-stock prevention.
- [x] Add newest-first product movement history.
- [x] Test adjustment success, rejection, rollback behavior, and history ordering.

### Phase 5: Delivery and verification
**Status:** complete

- [x] Generate and apply an initial migration to a clean database.
- [x] Add Gunicorn, Docker, Compose, environment example, and operating documentation.
- [x] Run the complete pytest suite and migration verification.
- [x] Build the Docker image and smoke-test category/product/stock flows through the running API.
- [x] Update `AGENTS.md` with verified commands and remove scaffold-only guidance.

### Phase 6: CI/CD and supply-chain security
**Status:** complete

- [x] Separate runtime and CI dependencies and harden the production image.
- [x] Add pull-request and branch quality gates for lint, tests, and clean migrations.
- [x] Add secret, source, dependency, filesystem, CodeQL, and image vulnerability scans.
- [x] Publish tested images to Docker Hub only from `main`, `v*` tags, or approved manual runs.
- [x] Generate image provenance/SBOM and add Dependabot maintenance.
- [x] Document GitHub secrets, image tags, and release behavior.
- [x] Validate workflow syntax, all local gates, and the hardened image.

## Decisions

- API prefix is `/api/v1`; Swagger UI is served by Flask-Smorest.
- Product quantity starts at zero and changes only through the stock adjustment endpoint.
- Monetary values use SQLAlchemy `Numeric` and Marshmallow `Decimal`, serialized as strings.
- API errors use `{ "error": { "code", "message", "details" } }`.
- SQLite is used for development and isolated temporary SQLite files are used by tests.
- Docker Hub credentials are repository secrets; untrusted pull requests never receive or use them.
- Docker publication is downstream of all test and security jobs and uses BuildKit provenance plus SBOM attestations.

## Errors Encountered

| Error | Attempt | Resolution |
|---|---:|---|
| None | 0 | Not applicable |
| Duplicate patch section emptied `app/models/__init__.py` | 1 | Restored model exports and verified the file. |
| `pytest` could not import the local `app` package | 1 | Added the repository root to pytest's configured `pythonpath`. |
| `app.api` package shadowed the imported `api` extension | 1 | Aliased the extension as `smorest_api` in the application factory. |
| `import app.models` rebound the factory's local `app` variable | 1 | Removed the redundant import; route imports load all models for metadata discovery. |
| Flask `abort()` rejected custom API `code` values | 1 | Switched routes to Flask-Smorest's abort helper and retained centralized JSON formatting. |
| Docker image dependency download timed out | 1 | Added explicit pip timeout/retry settings to the image and rebuilt. |
| CI dependency audit found Flask and Marshmallow advisories | 1 | Upgraded Flask to 3.1.3 and Marshmallow to 4.1.2. |
| Bandit 1.8.6 cannot scan Python 3.14 syntax | 1 | Upgraded Bandit to 1.9.4; GitHub Actions uses Python 3.12. |
| Migration validation used a Windows-relative SQLite URI | 1 | Use an absolute temporary SQLite path in local verification; CI already uses `/tmp`. |
| Flask-Migrate has no `db current --check` option | 1 | Changed the workflow to use the supported `db check` drift validation command. |

## Next Step

CI/CD phase complete; configure GitHub repository secrets before the first Docker Hub publication.
