"""HTTP smoke tests use their own loopback server, not a deployed service."""

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.process = subprocess.Popen(
            [sys.executable, "-u", "app.py"],
            cwd=Path(__file__).resolve().parent.parent,
            env=dict(os.environ, HOST="127.0.0.1", PORT="0"),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        cls.addClassCleanup(cls.cleanup)
        line = cls.process.stdout.readline().strip()
        if not line.startswith("Bag End listening on "):
            raise RuntimeError(f"Test HTTP server did not start: {line}")
        cls.base = "http://127.0.0.1:" + line.rsplit(":", 1)[1]

    @classmethod
    def cleanup(cls):
        cls.process.terminate()
        cls.process.wait(timeout=5)
        cls.process.stdout.close()

    def test_home(self):
        with urlopen(self.base, timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"Hello, world!", response.read())

    def test_health(self):
        with urlopen(self.base + "/healthz", timeout=3) as response:
            self.assertEqual(json.load(response), {"status": "ok"})

    def test_head_has_no_body(self):
        with urlopen(Request(self.base, method="HEAD"), timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.read(), b"")

    def test_source_files_are_not_served(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(self.base + "/app.py", timeout=3)
        self.assertEqual(error.exception.code, 404)
