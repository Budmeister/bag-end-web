# Codex Cloud setup

Select only `Budmeister/bag-end-web` for this environment. The repository is
self-contained for coding, schema tests, and HTTP tests. It does not need the
Mac, the parent infrastructure directory, container management access, production
credentials, or a running external database.

## Setup instructions to paste into the environment conversation

> Prepare this Python repository for development. Use Python 3.13 (the code also
> supports Python 3.11+) and PostgreSQL 17 server/client tools. Ensure initdb,
> pg_ctl, and postgres are installed. If setup runs as root, ensure the package's
> unprivileged postgres OS account exists. Do not start a persistent/system
> PostgreSQL service. Run `sh scripts/setup.sh`, then
> `.venv/bin/python scripts/test.py` and verify all tests pass. The test script
> creates and removes its own local PostgreSQL cluster. No database secrets or
> external database connections are needed. Use synthetic fixtures only. Do not
> connect to the production Mac, Bazzite, bank APIs, or backup storage.

Review the prepared environment and publish it only after the complete test
command passes. The actual Codex Cloud instance must still be verified during
setup; local validation does not establish which OS packages it starts with.

The official workflow lets Codex prepare runtimes/tools from this conversation,
record an install script and start instructions, and publish the prepared
filesystem for later tasks. See [Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments).

## Commands

Install Python dependencies into the checkout's `.venv`:

```sh
sh scripts/setup.sh
```

PostgreSQL server binaries must already be installed. The script finds them on
PATH, through `pg_config --bindir`, or under `/usr/lib/postgresql/*/bin`.
For another installation layout, set `PG_BIN` to the server's bin directory.
Installing only `libpq` or the SQL client is insufficient; `initdb` and `pg_ctl`
are required. Root-run environments drop PostgreSQL processes to the postgres
OS account; the database server never runs as root.

Run the full HTTP and database suite:

```sh
.venv/bin/python scripts/test.py
```

For a targeted run, pass unittest arguments after `--`, for example:

```sh
.venv/bin/python scripts/test.py -- discover -s tests -p test_http.py -v
```

Start the current hello-world app:

```sh
sh scripts/start.sh
```

It serves `/` and `/healthz` on port 8080 and currently makes no database
connection. `HOST` and `PORT` override the bind address and port. The application
workflow and agent API will be implemented after the user provides the design.

## How the test database works

Every test command creates a randomly named private directory under `/tmp` and
initializes a completely new PostgreSQL cluster there. The server listens only
on that run's private Unix socket, not on TCP. The runner creates only
`bag_end_test`, supplies its connection string for that subprocess, and disposes
the entire cluster after success or an ordinary test failure. Tests require the
expected database/user, matching per-run marker, and matching server data
directory before initializing schema.

This does not need a reusable PostgreSQL service, fixed port, Podman network, or
shared volume. Concurrent runs use distinct clusters/sockets and do not share
roles or state. SQL migrations and fixtures come entirely from `database/` in
this repository. Test writes roll back and a subsequent run starts fresh.

The older isolated Podman `test-db` host remains supported for the optional Mac
development controller. Cloud tests should always use `scripts/test.py` rather
than pointing `TEST_DATABASE_URL` at an external database.

## Access and secrets

No application or database secrets are required. During environment preparation,
allow the package sources needed to install Python/PostgreSQL and packages from
PyPI. After dependencies are prepared, the tests require only local Unix sockets
and loopback HTTP. Do not add a tunnel or private-network connection to production.

Administrator-controlled runtime Compose, firewall, and deployment files remain
outside this repository. The cloud agent may edit application/test code without
receiving authority over the deployed app. No CI/CD runner or deployment
automation is included in this preparation.
