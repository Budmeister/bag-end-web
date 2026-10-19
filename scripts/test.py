#!/usr/bin/env python3
"""Run tests with a private, temporary PostgreSQL cluster; no Docker required."""

import argparse
import json
import os
from pathlib import Path
import pwd
import secrets
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent.parent


def postgres_bin():
    candidates = []
    if os.environ.get("PG_BIN"):
        candidates.append(Path(os.environ["PG_BIN"]))
    for name in ("initdb", "pg_config"):
        binary = shutil.which(name)
        if binary:
            if name == "pg_config":
                result = subprocess.run([binary, "--bindir"], capture_output=True, text=True)
                if result.returncode == 0:
                    candidates.append(Path(result.stdout.strip()))
            else:
                candidates.append(Path(binary).parent)
    candidates.extend(sorted(Path("/usr/lib/postgresql").glob("*/bin"), reverse=True))
    for directory in candidates:
        if all((directory / name).is_file() and os.access(directory / name, os.X_OK)
               for name in ("initdb", "pg_ctl", "postgres")):
            return directory
    raise RuntimeError(
        "PostgreSQL server binaries are missing. Install PostgreSQL 17 (preferred), "
        "or set PG_BIN to its bin directory; see CLOUD_SETUP.md."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-tools", action="store_true")
    parser.add_argument("test_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    binaries = postgres_bin()
    if args.check_tools:
        result = subprocess.run([str(binaries / "postgres"), "--version"], check=True)
        return result.returncode

    from psycopg.conninfo import make_conninfo

    # initdb refuses root. On root-run cloud VMs, drop only the PostgreSQL
    # subprocesses to the package's unprivileged postgres account.
    identity = {}
    if os.geteuid() == 0:
        try:
            account = pwd.getpwnam("postgres")
        except KeyError as error:
            raise RuntimeError("Root-run tests require the unprivileged postgres OS account") from error
        identity = {"user": account.pw_uid, "group": account.pw_gid, "extra_groups": []}

    def pg(command, *options, check=True):
        result = subprocess.run(
            [str(binaries / command), *options], cwd="/tmp", capture_output=True,
            text=True, **identity,
        )
        if check and result.returncode:
            raise RuntimeError(f"{command} failed: {result.stderr.strip()} {result.stdout.strip()}")
        return result

    # Keep the socket path short enough for Unix's socket pathname limit.
    with tempfile.TemporaryDirectory(prefix="bag-end-tests-", dir="/tmp") as temporary:
        directory = Path(temporary)
        data = directory / "data"
        sockets = directory / "socket"
        sockets.mkdir(mode=0o700)
        if identity:
            os.chown(directory, identity["user"], identity["group"])
            os.chown(sockets, identity["user"], identity["group"])
        run_id = secrets.token_hex(16)
        (directory / "disposable.json").write_text(json.dumps({
            "run_id": run_id, "data_directory": str(data), "socket_directory": str(sockets),
        }))
        pg("initdb", "-D", str(data), "--username=bag_end_test_admin", "--auth-local=trust",
           "--auth-host=reject", "--encoding=UTF8", "--no-locale")
        with (data / "postgresql.conf").open("a") as configuration:
            configuration.write(
                "\nlisten_addresses = ''\n"
                f"unix_socket_directories = '{str(sockets).replace(chr(39), chr(39)*2)}'\n"
                "unix_socket_permissions = 0700\n"
            )
        try:
            pg("pg_ctl", "-D", str(data), "-l", str(directory / "postgres.log"), "-w", "-t", "30", "start")
            environment = {
                key: value for key, value in os.environ.items()
                if not key.startswith("PG") and key not in {"DATABASE_URL", "TEST_DATABASE_URL"}
            }
            environment.update(
                PYTHONDONTWRITEBYTECODE="1",
                TEST_DATABASE_URL=make_conninfo(
                    host=str(sockets), dbname="bag_end_test", user="bag_end_test_admin", connect_timeout=5,
                ),
                TEST_DATABASE_RUN_ID=run_id,
                TEST_DATABASE_DATA_DIR=str(data),
            )
            # Create only the explicitly named test DB, on our private socket.
            import psycopg
            with psycopg.connect(
                host=str(sockets), dbname="postgres", user="bag_end_test_admin", autocommit=True,
            ) as connection:
                connection.execute("CREATE DATABASE bag_end_test")
            options = args.test_args
            if options[:1] == ["--"]:
                options = options[1:]
            print("Running tests with disposable PostgreSQL (private Unix socket; no TCP listener)", flush=True)
            return subprocess.run(
                [sys.executable, "-m", "unittest", *(options or ["discover", "-s", "tests", "-v"])],
                cwd=ROOT, env=environment,
            ).returncode
        finally:
            pg("pg_ctl", "-D", str(data), "-m", "immediate", "-w", "-t", "30", "stop", check=False)
            print("Disposed temporary PostgreSQL cluster and synthetic test data", flush=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ImportError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
