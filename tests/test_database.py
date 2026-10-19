"""Migrations/constraints against a fresh, explicitly disposable database."""

from decimal import Decimal
import json
import os
from pathlib import Path
import unittest

import psycopg
from psycopg.conninfo import conninfo_to_dict


ROOT = Path(__file__).resolve().parent.parent


def test_connection_string():
    url = os.environ.get("TEST_DATABASE_URL", "")
    settings = conninfo_to_dict(url)
    if (settings.get("dbname"), settings.get("user")) != ("bag_end_test", "bag_end_test_admin"):
        raise RuntimeError("Tests require the isolated bag_end_test database and test administrator")
    host = settings.get("host", "")
    if host == "test-db":
        return url  # Existing isolated Podman test service.
    socket = Path(host)
    if not socket.is_absolute() or not socket.parent.name.startswith("bag-end-tests-"):
        raise RuntimeError("Tests refuse non-disposable database hosts")
    marker = socket.parent / "disposable.json"
    try:
        declaration = json.loads(marker.read_text())
    except (OSError, ValueError) as error:
        raise RuntimeError("Disposable database marker is missing or invalid") from error
    if (declaration.get("run_id") != os.environ.get("TEST_DATABASE_RUN_ID") or
        declaration.get("data_directory") != os.environ.get("TEST_DATABASE_DATA_DIR") or
        declaration.get("socket_directory") != str(socket)):
        raise RuntimeError("Disposable database declaration does not match this test run")
    return url


def setUpModule():
    with psycopg.connect(test_connection_string(), autocommit=True) as connection:
        identity = connection.execute("SELECT current_database(), current_user").fetchone()
        if identity != ("bag_end_test", "bag_end_test_admin"):
            raise RuntimeError("Refusing to initialize a non-test database")
        expected_directory = os.environ.get("TEST_DATABASE_DATA_DIR")
        if expected_directory:
            actual_directory = connection.execute("SHOW data_directory").fetchone()[0]
            if Path(actual_directory).resolve() != Path(expected_directory).resolve():
                raise RuntimeError("Connected PostgreSQL is not the runner's disposable cluster")
        # Fail rather than reset any existing schema. Each run requires a fresh DB.
        if connection.execute("SELECT to_regnamespace('bag_end')").fetchone()[0] is not None:
            raise RuntimeError("Test database is not fresh; recreate test-db")
        for role in ["owner", "web", "tools", "importer", "backup", "migrator"]:
            connection.execute(f"CREATE ROLE bag_end_{role} NOLOGIN")
        connection.execute("CREATE SCHEMA bag_end AUTHORIZATION bag_end_owner")
        connection.execute("GRANT USAGE ON SCHEMA bag_end TO bag_end_web, bag_end_tools, bag_end_importer, bag_end_backup")
        connection.execute("SET ROLE bag_end_owner")
        for migration in sorted((ROOT / "database/migrations").glob("*.sql")):
            with connection.transaction():
                connection.execute(migration.read_text())
        connection.execute("RESET ROLE")
        connection.execute((ROOT / "database/fixtures/synthetic.sql").read_text())


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db = psycopg.connect(test_connection_string())
        self.addCleanup(self.db.close)
        self.addCleanup(self.db.rollback)

    def insert(self, kind="REGULAR", pool=None, note=None):
        return self.db.execute(
            "INSERT INTO bag_end.transactions(type,pool_id,date,amount,merchant,note) "
            "VALUES (%s,%s,'2026-01-01',%s,'Synthetic test merchant',%s) RETURNING id",
            (kind, pool, Decimal("-0.30"), note),
        ).fetchone()[0]

    def test_synthetic_fixtures(self):
        self.assertEqual(self.db.execute("SELECT count(*) FROM bag_end.transactions").fetchone()[0], 4)

    def test_pool_and_note_are_optional_and_money_is_decimal(self):
        identifier = self.insert()
        self.assertEqual(self.db.execute(
            "SELECT pool_id,note,amount FROM bag_end.transactions WHERE id=%s", (identifier,)
        ).fetchone(), (None, None, Decimal("-0.30")))

    def test_invalid_type_is_rejected(self):
        with self.assertRaises(psycopg.errors.CheckViolation):
            self.insert(kind="INVALID")

    def test_missing_pool_is_rejected(self):
        with self.assertRaises(psycopg.errors.ForeignKeyViolation):
            self.insert(pool="ffffffff-ffff-4fff-8fff-ffffffffffff")

    def test_web_can_write_without_owning_schema(self):
        self.db.execute("SET ROLE bag_end_web")
        self.insert(kind="PAYDAY", note="Synthetic note")
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):
            self.db.execute("CREATE TABLE bag_end.forbidden(id integer)")

    def test_importer_preserves_user_assignments(self):
        identifier = self.insert(note="Keep this synthetic note")
        self.db.execute("SET ROLE bag_end_importer")
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):
            self.db.execute("UPDATE bag_end.transactions SET pool_id=NULL WHERE id=%s", (identifier,))
