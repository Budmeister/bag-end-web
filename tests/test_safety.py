"""Guard against accidentally directing integration tests at persistent data."""

import os
import unittest
from unittest.mock import patch

from test_database import test_connection_string


class DatabaseSafetyTests(unittest.TestCase):
    def test_persistent_database_is_rejected(self):
        with patch.dict(os.environ, {"TEST_DATABASE_URL": "postgresql://bag_end_web@bag-end-db/bag_end"}):
            with self.assertRaises(RuntimeError):
                test_connection_string()

    def test_arbitrary_tcp_host_is_rejected_even_with_test_names(self):
        with patch.dict(os.environ, {"TEST_DATABASE_URL": "postgresql://bag_end_test_admin@127.0.0.1/bag_end_test"}):
            with self.assertRaises(RuntimeError):
                test_connection_string()

    def test_unmarked_socket_is_rejected(self):
        with patch.dict(os.environ, {"TEST_DATABASE_URL": "host=/tmp dbname=bag_end_test user=bag_end_test_admin"}):
            with self.assertRaises(RuntimeError):
                test_connection_string()
