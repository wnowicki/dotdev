# FastAPI Engineering Standard

Status: Version 1.0  
Scope: New FastAPI projects and incremental modernization of existing projects

## 1. Purpose

This standard defines the shared engineering baseline for FastAPI applications. It combines practices proven across focused AI services, relational products, public multi-tenant APIs, and ML/background-processing systems.

The standard is intentionally adaptive:

- new projects follow it from inception;
- existing projects adopt it incrementally when affected code is materially changed;
- project-specific decisions override defaults only when documented;
- architecture must remain proportional to the project;
- mechanical rules should be enforced by tooling rather than prose alone.

The terms **must**, **should**, and **may** indicate requirement, preferred default, and permitted option respectively.

## 2. Core principles

- Choose the smallest architecture that keeps responsibilities and dependencies clear.
- Keep transport, business logic, persistence, and external integrations separate.
- Make lifecycle, transaction, security, and failure behavior explicit.
- Validate data at every untrusted boundary.
- Prefer composition and dependency injection over hidden global construction.
- Optimize for maintainability and operational correctness, not architectural ceremony.
- Do not reorganize stable code merely for conformity; migrate when there is material value.

## 3. Approved project structures

### 3.1 Focused service

Use a layer-oriented structure for a small service with a narrow purpose and few business concepts:

```text
app/
├── main.py
├── application.py
├── core.py
├── admin/
│   ├── base.py
│   └── main.py
├── api/
│   ├── dependencies.py
│   ├── error_handlers.py
│   ├── middleware.py
│   ├── router.py
│   └── routes/
├── models/
├── services/
├── repositories/
│   └── base.py
├── gateways/
└── infrastructure/

tests/
├── unit/
├── integration/
├── contract/
└── fixtures/
```

### 3.2 Substantial product

Use feature-oriented modules for a product with several independently evolving business capabilities:

```text
app/
├── main.py
├── application.py
├── core.py
├── admin/
│   ├── base.py
│   └── main.py
├── api/
│   ├── dependencies.py
│   ├── error_handlers.py
│   ├── middleware.py
│   ├── health.py
│   └── router.py
├── features/
│   ├── feature_name/
│   │   ├── api.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   ├── tables.py
│   │   └── errors.py
│   └── another_feature/
├── infrastructure/
│   ├── database/
│   ├── clients/
│   └── telemetry/
├── ui/
├── cli/
└── workers/

tests/
├── features/
├── integration/
├── contract/
├── migrations/
└── fixtures/
```

### 3.3 Structure rules

- A feature must have one obvious home.
- Business rules must not be duplicated across API, UI, CLI, and workers.
- Transport adapters must not contain persistence queries or core business rules.
- Features must not import another feature's private persistence implementation.
- Cross-feature behavior must use an explicit service or public feature interface.
- Avoid generic dumping grounds such as `utils.py`, `helpers.py`, and an oversized `core.py`.
- Create modules when responsibilities exist; do not create speculative empty layers.
- `app/` is the default for deployable applications. Use `src/<package>/` when building an installable library, multiple distributions, or when import isolation provides concrete value.
- Existing repositories do not need structural migration without a substantive reason.

## 4. Architecture and dependency direction

- FastAPI routes depend on application services or use cases.
- Application services coordinate business rules, authorization, repositories, and gateways.
- Repositories isolate persistence queries.
- Gateways isolate external APIs, search engines, LLM providers, email, object storage, and similar systems.
- Domain and application logic must not import FastAPI.
- Concrete infrastructure dependencies should be injected rather than constructed inside business operations.
- Repository protocols are optional. Use them when multiple implementations, legacy boundaries, isolated testing, or strong dependency inversion justify them.
- Public persistence-independent models are required when persistence entities contain private or internal fields.

## 5. Python and dependencies

- Use `uv` and commit `uv.lock`.
- Run project tools through `uv run`.
- CI and production builds must use frozen dependency installation.
- Separate production and development dependencies. Add optional groups for load tests, ML, or operational tools when useful.
- Each repository chooses an approved stable Python version.
- `pyproject.toml`, `.python-version`, Ruff, CI, containers, and documentation must agree on supported Python versions.
- Do not maintain compatibility matrices that are neither required nor tested.
- Dependency additions and updates must include lock-file changes and pass the full quality pipeline.

## 6. Application construction and lifecycle

- New projects must use an application factory.
- `main.py` should expose the production application and contain minimal logic.
- `application.py` should act as the composition root for middleware, exception handlers, routers, and lifecycle resources.
- Long-lived resources must be created and closed through FastAPI lifespan or another explicit lifecycle owner.
- This includes database engines, HTTP clients, Elasticsearch/OpenSearch clients, Redis, LLM clients, and integration gateways.
- Imports must not open network connections, databases, or log files.
- Reusable dependencies should use typed `Annotated` aliases.
- Router prefixes, tags, and shared dependencies should be declared on `APIRouter` where applicable.

## 7. Sync, async, and concurrency

- Synchronous relational persistence is the default for new projects unless end-to-end asynchronous I/O has a demonstrated benefit.
- Synchronous stacks should use synchronous FastAPI route functions.
- `async def` should be used only when the relevant call chain is non-blocking.
- Blocking I/O must not execute directly on the event loop.
- When blocking dependencies cannot be replaced, use an explicit and bounded thread boundary.
- External fan-out must be bounded.
- Long operations must define timeouts, cancellation, resource cleanup, and graceful shutdown behavior.

## 8. API contracts

- Every externally consumed endpoint must declare validated request and explicit public response schemas.
- Persistence models containing internal or sensitive fields must not be returned directly.
- Separate persistence/table, create, partial-update, public response, domain, and external DTO models where those concepts differ.
- Partial updates should use optional fields and `exclude_unset`.
- Collection endpoints must enforce page-size bounds and deterministic ordering.
- Every project must select and document one pagination contract.
- APIs must use a stable, sanitized error envelope with a machine-readable code, safe message, and request ID.
- Exception-to-HTTP translation should be centralized.
- Invalid input, authentication failure, authorization failure, missing resources, conflicts, dependency failure, timeout, and unexpected failure must remain distinguishable where relevant.
- Public APIs must explicitly define versioning, compatibility, deprecation, idempotency, and optimistic-concurrency policies.
- Select the representation format based on the project. Prefer JSON:API for larger public-facing resource APIs with rich relationships and long-lived external consumers; do not require it universally.

## 9. Models and validation

- Use Pydantic at HTTP, configuration, external API, search-document, worker-message, and structured LLM-output boundaries.
- Public models should be explicit and reject unintended fields unless extensibility is deliberate.
- Centralize reusable constrained types for identifiers, email, UTC datetimes, pagination, and domain codes.
- Nullable fields must use explicit optional types.
- Generated, mutable, and time-dependent defaults must use `default_factory`.
- Use timezone-aware UTC internally and at persistence boundaries.
- Serialize datetimes consistently using ISO 8601.
- Do not rely on the host's local timezone.

## 10. Persistence and transactions

- Request-scoped sessions must be yielded and reliably closed.
- Workers, CLI commands, and scheduled jobs must use explicit context-managed sessions.
- Do not acquire sessions using `next(get_session())`.
- The application service or use case should normally own commit and rollback.
- Repositories should normally flush rather than commit.
- Generic CRUD methods must not perform hidden commits.
- A repository or adapter may own a transaction only when the operation is explicitly atomic, self-contained, clearly documented, and not expected to join a larger business transaction.
- Introduce a unit of work when multi-repository coordination justifies it; do not mandate it for simple operations.
- Relational projects must use Alembic or an explicitly approved equivalent.
- Autogenerated migrations must be reviewed.
- CI must verify upgrading an empty database to the current migration head.
- Database-specific queries and migrations must be tested against the production database family.
- Externally owned schemas should be isolated and treated as read-only unless ownership is explicit.

## 11. Security

- Secrets must come from typed settings or an approved secret provider.
- Secret-bearing `.env` files must not be committed.
- Example environment files contain names and safe placeholders only.
- Production startup must reject known example secrets, missing mandatory credentials, debug settings, and unsafe CORS configuration.
- Never log credentials, passwords, bearer tokens, session identifiers, secret settings, or private data without an explicit approved policy.
- CORS must be configured explicitly per environment. Wildcard origins must not be combined with credentialed requests.
- M2M services should omit CORS unless a browser consumer exists.
- Authorization, ownership, consent, and tenant rules must be enforced below the transport layer.
- Security enforcement outside the application must be documented.
- CI should include dependency, secret, and container scanning.

### 11.1 Credentials

- Generate high-entropy opaque credentials.
- Persist only credential hashes.
- Reveal raw credentials only once.
- Support expiry, revocation, and rotation where the threat model requires them.
- Use modern password hashing and timing-safe, non-revealing authentication behavior.

### 11.2 Multi-tenancy

- Resolve tenant context from trusted authentication data, not client-supplied tenant identifiers.
- Scope every tenant-owned repository operation structurally.
- Prevent downstream calls or writes until ownership is established.
- Hide cross-tenant resource existence with `404` when appropriate.
- Test tenant isolation and negative authorization paths explicitly.

## 12. External integrations

Each integration must define:

- typed request and response models;
- connection and operation timeouts;
- retry and backoff behavior;
- retryable and terminal failure categories;
- idempotency implications;
- error translation;
- lifecycle and cleanup;
- logging, metrics, and redaction;
- partial-failure behavior.

Reuse clients, validate responses, bound fan-out, and distinguish missing data from dependency unavailability. Do not use excessive retries to conceal a dependency that violates the endpoint latency budget.

## 13. AI and LLM profile

When using LLMs:

- isolate provider SDKs behind gateways;
- validate structured output;
- version prompts as product behavior;
- define model allowlists, timeout, retries, concurrency, token limits, cost budgets, and fallback behavior;
- capture model, prompt version, token usage, duration, and result status where permitted;
- use fixture-backed regression tests for malformed model and source-data output;
- do not log full prompts, documents, or responses without an explicit data-handling decision.

## 14. Background jobs and ML profile

- Separate heavyweight and ordinary workloads when their operational characteristics differ.
- Define task idempotency, retryable failures, time limits, typed results or persisted status, and graceful shutdown.
- Propagate request and trace context into jobs.
- Failed jobs must fail observably; do not return an error payload that causes the queue to record success.
- Store large artifacts in object storage rather than images or local container state.
- Record model provenance and build metadata.
- Keep training workloads separate from request-serving processes.
- Define memory and concurrency budgets.

## 15. Errors and resilience

- Define application/domain and infrastructure exception families.
- Translate vendor exceptions at adapter boundaries.
- Translate application exceptions into HTTP or worker-specific responses centrally.
- Never map all unexpected dependency failures to `404`.
- Define timeout, retry, cancellation, and rollback behavior for failure-sensitive operations.
- Unexpected client-facing errors must not reveal stack traces, queries, credentials, or vendor response bodies.

## 16. Observability

- New projects must produce structured JSON logs and request IDs.
- Containerized applications must log to stdout/stderr.
- Avoid local rotating files unless the deployment explicitly collects them.
- Use parameterized logging and centralized redaction.
- Validate or replace incoming request IDs according to a documented trust policy.
- Propagate correlation to outbound calls, jobs, audit records, and usage records.
- Provide shallow liveness and dependency-aware readiness endpoints.
- Deployed services must expose request count, latency, errors, and dependency health metrics.
- Worker services should expose queue depth and task outcomes.
- Use OpenTelemetry-compatible instrumentation for traces and metrics.
- Instrument FastAPI, outbound HTTP, persistence, Redis, and workers where applicable.
- Exporters are environment-specific; local development and tests must work without a collector.
- Distributed tracing may remain disabled for small deployments, but instrumentation should be configurable without redesign.
- Telemetry must not capture sensitive payloads by default.

## 17. Testing

- Use pytest and add async support only for async behavior.
- Test observable success and relevant failure paths.
- Every production defect fix must include a focused regression test.
- Use committed fixtures for complex and malformed real-world data.
- Tests must be deterministic and isolated, and must close engines and clients.
- Override FastAPI dependencies explicitly in API tests.
- Mock integrations at adapter boundaries and add critical integration or contract tests where feasible.
- Database projects must test repository behavior, rollback, migrations, and database-specific behavior.
- Public APIs must test response and error contracts and should validate OpenAPI compatibility.
- Security-sensitive features must include negative-path tests.
- There is no universal numerical coverage threshold. Projects may set thresholds based on risk; changed behavior and critical paths must be covered regardless of percentage.

## 18. Quality tooling

- Use Ruff for formatting, imports, linting, FastAPI rules, and baseline security checks.
- Static type checking is mandatory.
- Prefer `ty` for new projects when compatible with the selected framework and libraries.
- Combine `ty` with appropriate Ruff `ANN` and `PYI` rules.
- Existing mypy projects may retain mypy until a verified migration is worthwhile.
- Do not retain two type checkers permanently without demonstrated value.
- Use one pinned tool configuration locally, in pre-commit, and in CI.
- CI must run `ruff check`, `ruff format --check`, type checking, and tests.
- Add migration, security, documentation, and container checks when applicable.
- Suppressions must be narrow and use rule codes; explain non-obvious exceptions.
- Remove obsolete tooling configuration when a tool has been replaced.

## 19. Containers and delivery

- Use a pinned base image compatible with the declared Python version.
- Install from the frozen lock file.
- Build cache-efficient images and copy only required runtime files.
- Run as a non-root user.
- Avoid floating production image and tool tags.
- Log to stdout/stderr and do not assume persistent writable storage.
- Support graceful termination.
- Provide appropriate liveness and readiness probes.
- Run migrations as an explicit deployment operation, not an import-time side effect.
- Required quality gates must pass before publishing deployable images.
- Pin CI actions according to the organization's supply-chain policy.
- Document rollback and post-deployment verification.

## 20. Documentation and workflow

Each repository must document:

- purpose and consumers;
- architecture and important boundaries;
- supported Python version;
- setup and local execution;
- environment variables;
- test, lint, format, and type-check commands;
- migrations and seed data;
- containers and deployment entrypoints;
- workers and scheduled tasks;
- health endpoints and authentication model;
- definition of done.

Documentation must distinguish read-only checks, automatic fixes, generated changes, and destructive/reset commands. Destructive commands require explicit safeguards.

Consequential architecture decisions should use short ADRs containing context, decision, consequences, and scope. Documentation and `AGENTS.md` must describe the current repository, not an aspirational future state.

## 21. Standard project profiles

Start with the Core profile and add only profiles the project needs:

| Profile | Additional requirements |
|---|---|
| Core FastAPI | Settings, factory, lifespan, error contract, observability, health, Ruff, type checker, pytest, Docker, CI |
| Relational CRUD | SQLModel/SQLAlchemy, transaction ownership, Alembic, migration tests |
| Public API | Versioning, stable errors, contract tests, authentication scopes, rate limits, request IDs |
| Multi-tenant SaaS | Credential-derived tenant context, scoped repositories, isolation tests |
| JSON:API | Media types, serializers, relationships, includes, JSON:API errors |
| Search-backed | Search gateway, validated documents, bounded queries, readiness checks |
| AI/LLM | Provider gateway, prompt versions, structured output, usage and cost controls |
| Worker/ML | Queue policy, idempotency, retries, task state, artifact storage |
| Embedded admin/UI | Exposure controls, session security, CSRF analysis, audit trail |

## 22. Definition of done

A change is complete when applicable:

- behavior and acceptance criteria are implemented;
- architecture and dependency rules are preserved;
- success, failure, authorization, and regression tests are present;
- Ruff formatting and lint checks pass;
- static type checking passes;
- migrations are reviewed and tested;
- public contracts and documentation are updated;
- configuration examples are updated without secrets;
- security and privacy implications are addressed;
- observability is sufficient to operate the change;
- the container builds and relevant CI checks pass;
- no unrelated cleanup or speculative abstractions were introduced.

## 23. Explicitly discouraged patterns

Do not introduce without a documented exception:

- mismatched Python versions across metadata, CI, and runtime;
- floating `latest` production images;
- root container execution;
- import-time connections or file handlers;
- per-request unclosed integration clients;
- `next(get_session())` session acquisition;
- hidden repository commits;
- blocking I/O directly inside async routes;
- evaluated timestamp or mutable model defaults;
- returning private persistence models publicly;
- wildcard credentialed CORS;
- raw token or session logging;
- broad exceptions translated to `404`;
- failed tasks reported as successful results;
- unbounded list endpoints or fan-out;
- generic dumping-ground modules;
- stale documentation presented as current architecture.
