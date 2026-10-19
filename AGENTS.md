# Bag End Web — development instructions

## Scope and design

This repository is the application source, schema migrations, and synthetic
tests. The user has not provided the budgeting workflow or UI design yet.
Do not invent allocation, rollover, account, or pool semantics from the initial
schema. No Containerfiles or image-build workflow are wanted.

The initial transaction columns are type (`PAYDAY`/`REGULAR`), optional pool
foreign key, date, signed decimal amount, merchant, and optional note. Existing
applied migrations must not be edited; add new numbered migrations.

## Setup and tests

- Read `CLOUD_SETUP.md` for the cloud environment prerequisites.
- Install development dependencies with `sh scripts/setup.sh`.
- Run the complete suite with `.venv/bin/python scripts/test.py`.
- This command creates its own PostgreSQL cluster, applies migrations, loads
  synthetic fixtures, runs tests, and removes the cluster. No Docker, Podman,
  parent checkout, external SQL endpoint, or database credentials are needed.
- Start the current app with `sh scripts/start.sh`; it listens on port 8080
  by default and has a `/healthz` endpoint. The hello-world app needs no database.
- The standard-library `unittest` runner and pinned Psycopg packages are used.
- Tests must fail when required database tools are missing; do not skip the DB
  suite or substitute SQLite to make checks pass.

## Financial and infrastructure boundaries

- Use code and synthetic data only. Never request or ingest real transactions,
  production dumps, bank tokens, financial inference prompts, production
  credentials, or financial logs in a cloud development task.
- Do not connect to the Mac's persistent PostgreSQL, Bazzite inference, bank
  accounts, backup storage, or production application endpoints.
- Runtime Compose definitions, firewall policy, production role credentials,
  deployment controls, and the container management socket are administered
  outside this repository. Do not add mounts or connections to reach them.
- Development/test scripts in this repository control disposable resources
  only. Never run destructive schema tests against a reusable database.
- Runtime deployment is separate from development. A code change does not
  authorize changing protections, credentials, network permissions, or deployment.

## Agreed agent API direction (implement later)

- There will be no separate tools service. Web owns SQL and the controlled
  financial API; the categorization agent has no direct database connection.
- Agent initiates authenticated HTTP requests to web to claim categorization
  jobs, heartbeat leases, and submit assignments. Web validates and immediately
  applies assignments, audits them, and preserves newer manual changes.
- Jobs need leases, safe retries, and recovery after agent failure. What creates
  categorization jobs has not been decided yet.
- Expose an authenticated agent-facing OpenAPI document with ETag and API
  revision discovery. Breaking changes may require an agent update.
- Agent calls inference separately. Idle HTTP polling/heartbeats must not
  invoke inference, so the LLM can unload after inactivity.
- Implement the web contract first. The agent container will be configured later.
