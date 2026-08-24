# AGENTS.md — FastAPI Project Template

Adapt bracketed sections to the repository. Remove irrelevant sections rather than leaving speculative instructions.

## Project context

- Purpose: `[describe the service or product]`
- Consumers: `[public API / internal API / browser UI / workers / CLI]`
- Architecture: `[focused layered service / feature-oriented modular product]`
- Enabled profiles: `[Core, Relational CRUD, Public API, Multi-tenant, JSON:API, Search, AI/LLM, Worker/ML, Admin/UI]`
- Python: `[version]`
- Package manager: `uv`

Read the README and relevant architecture documentation before making consequential changes. Describe the current implementation accurately; do not treat planned architecture as already implemented.

## Canonical commands

- Install: `[uv sync --frozen / repository command]`
- Run: `[uv run fastapi dev ... / repository command]`
- Tests: `[uv run pytest ...]`
- Lint: `uv run ruff check .`
- Format check: `uv run ruff format --check .`
- Format: `uv run ruff format .`
- Type check: `[uv run ty check / uv run mypy ...]`
- Migrations: `[repository commands]`
- All non-mutating checks: `[repository command]`

Use locked project tools. Distinguish check-only commands from commands that modify files, generate migrations, reset data, or contact external systems.

## Structure and boundaries

- Keep FastAPI transport, business behavior, persistence, and integrations separate.
- Routes validate input, resolve trusted context, call an application operation, and serialize the response.
- Do not place business rules or persistence queries in routes, UI pages, CLI commands, or workers.
- Domain and application code must not depend on FastAPI.
- Construct dependencies in the application composition root and inject them into services.
- Do not create generic dumping grounds such as `utils.py`, `helpers.py`, or an oversized `core.py`.
- Give each feature one obvious home. Do not create speculative empty abstractions.
- Cross-feature behavior must use explicit public services or contracts, not another feature's private persistence code.

## FastAPI lifecycle

- Use the application factory in `[path]`.
- Manage engines and long-lived HTTP, search, Redis, LLM, and other clients through lifespan.
- Close resources during shutdown.
- Avoid import-time I/O and global mutable resource construction.
- Use typed `Annotated` aliases for reusable dependencies.

## Sync and async

- Use synchronous route functions with synchronous persistence or integrations.
- Use `async def` only when the relevant call path is non-blocking.
- Never run blocking I/O directly on the event loop.
- Bound concurrent fan-out and define timeout and cancellation behavior.

## Models and API contracts

- Validate all HTTP and external-system boundaries with typed Pydantic models.
- Declare explicit public response models for externally consumed endpoints.
- Do not expose persistence models containing private or internal fields.
- Use explicit optional types and `default_factory` for dynamic or mutable defaults.
- Use timezone-aware UTC internally.
- Bound collection endpoints and preserve deterministic ordering.
- Follow the repository's selected pagination, error, versioning, and representation contracts.
- Add or update OpenAPI and contract tests when public behavior changes.

## Persistence and transactions

- Use yielded request sessions and context-managed sessions outside requests.
- Application services or use cases normally own commit and rollback.
- Repositories normally flush and must not hide commits in generic CRUD methods.
- An atomic repository-owned transaction requires an explicit contract and documented justification.
- Review generated migrations and test upgrading an empty database to head.
- Test database-specific behavior against the production database family.

## Security and privacy

- Never commit or print secrets.
- Never log passwords, tokens, session identifiers, credentials, or sensitive payloads.
- Resolve authorization, ownership, consent, and tenant rules below the transport layer.
- Derive tenant context from trusted authentication data; do not accept tenant overrides from clients.
- Configure CORS explicitly and never combine wildcard origins with credentials.
- Preserve sanitized errors and cross-tenant resource-hiding behavior.
- Consider whether logs, traces, metrics, prompts, and fixtures contain sensitive data.

## Integrations

- Put external systems behind typed gateways or adapters.
- Reuse clients and define timeouts, retries, idempotency, error translation, lifecycle, and partial-failure behavior.
- Validate external responses.
- Do not translate every dependency failure into not-found.

## Observability

- Use structured, parameterized logs and the repository's redaction rules.
- Generate or safely accept request IDs and propagate correlation to outbound calls and jobs.
- Preserve shallow liveness and dependency-aware readiness semantics.
- Use OpenTelemetry-compatible instrumentation where configured.
- Local development and tests must not require an external telemetry collector.

## Testing

- Add tests for observable success and relevant failure paths.
- Every defect fix requires a focused regression test.
- Include negative authorization and tenant-isolation cases for security-sensitive behavior.
- Mock integrations at adapter boundaries; use integration or contract tests for critical dependencies.
- Keep tests deterministic and close engines and clients.
- Do not pursue coverage percentage at the expense of meaningful behavior tests.

## Quality and change discipline

- Run Ruff formatting, Ruff linting, the selected type checker, and relevant tests before completion.
- Use narrow, coded suppressions and explain non-obvious exceptions.
- Preserve unrelated user changes.
- Do not refactor unrelated code or add speculative abstractions.
- Update documentation, configuration examples, schemas, migrations, and operational guidance when behavior changes.
- Record consequential architectural departures in an ADR or equivalent decision note.

## Definition of done

Before declaring work complete, confirm that applicable:

- acceptance behavior works;
- architecture boundaries remain intact;
- success, failure, authorization, and regression tests pass;
- lint, format, and type checks pass;
- migrations and public contracts are correct;
- secrets and sensitive data remain protected;
- observability supports operating the change;
- documentation describes the resulting implementation;
- no unrelated changes were introduced.

## Repository-specific constraints

`[Add only concrete constraints, commands, exceptions, and verification requirements that apply to this repository.]`
