# Architecture Decisions

## ADR-001

**Decision:** Use PostgreSQL as the relational data store for production workloads.

**Reason:** PostgreSQL provides strong consistency, mature tooling, and broad production adoption for document metadata and application state.

**Status:** Accepted

## ADR-002

**Decision:** Use FastAPI with Pydantic v2 and pydantic-settings for backend configuration and validation.

**Reason:** This stack offers strong typing, automatic validation, and clear configuration management for enterprise-style services.

**Status:** Accepted

## ADR-003

**Decision:** Keep authentication and database logic out of the initial configuration layer.

**Reason:** The current step focuses on environment-driven configuration, logging, and application structure without introducing runtime behavior too early.

**Status:** Accepted

## ADR-004

**Decision:** Use SQLAlchemy 2.x ORM models with Alembic migrations for the DocuChat database layer.

**Reason:** SQLAlchemy 2.x provides typed ORM models and mature PostgreSQL support, while Alembic gives repeatable schema migrations instead of manual table creation.

**Status:** Accepted

## ADR-005

**Decision:** Provide a local PostgreSQL service through Docker Compose.

**Reason:** A reproducible local database makes migrations, authentication, document metadata, and chat history easier to test consistently across development machines.

**Status:** Accepted
