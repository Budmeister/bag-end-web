# Bag End Web

A basic Python hello-world web service. It uses only the standard library;
there are no packages to install, build steps, or Containerfiles.

Run from the repository root with Python 3.11 or newer (3.13 recommended):

```sh
sh scripts/start.sh
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080) to see **Hello, world!**.
`GET /healthz` returns `{"status":"ok"}`. Other paths return 404. GET and HEAD
are supported. No database connection or credentials are needed for this app.

The service binds `0.0.0.0:8080` by default for container networking. Override
`HOST` or `PORT` when needed, for example for a loopback-only local run:

```sh
HOST=127.0.0.1 PORT=8081 sh scripts/start.sh
```

The parent Compose setup should use `docker.io/library/python:3.13-bookworm`,
clone this repository, and execute `scripts/start.sh`. The full Bookworm image
provides Python and Git. The hello-world service makes no outbound requests
and serves no filesystem content. Request access logging is disabled.

CI/CD and the self-hosted runner are not configured yet.

## Development and tests

For Codex Cloud, follow [CLOUD_SETUP.md](CLOUD_SETUP.md). Install Python and
PostgreSQL server tools during environment preparation, then run entirely from
this repository:

```sh
sh scripts/setup.sh
.venv/bin/python scripts/test.py
```

The test runner starts a fresh private PostgreSQL cluster, applies migrations,
loads synthetic fixtures, runs the unittest suite, and removes the cluster.
It needs no Docker/Podman, parent checkout, reusable database, or credentials.
The PostgreSQL server listens on a private Unix socket and never on a TCP port.

For the optional Mac-only development container, the separately administered
parent workspace has `scripts/development.py up`, `sync`, and `test` commands.
Those are not prerequisites for cloud work. Its preview uses port 8081.

The development dependencies are pinned in `requirements-dev.txt`. The normal
hello-world runtime still requires only Python's standard library.

The initial PostgreSQL schema and synthetic fixtures are documented in
[database/README.md](database/README.md). Production provisioning and credentials
are administered separately; the hello-world HTTP service still runs without a
database connection. See [AGENTS.md](AGENTS.md) for synthetic-data boundaries and
the agreed future agent API direction. The budgeting design is not finalized.
