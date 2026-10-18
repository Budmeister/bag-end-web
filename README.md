# Bag End Web

A basic Python hello-world web service. It uses only the standard library;
there are no packages to install, build steps, or Containerfiles.

Run from the repository root with Python 3.13 or newer:

```sh
sh scripts/start.sh
```

Open [http://localhost:8080](http://localhost:8080) to see **Hello, world!**.
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
