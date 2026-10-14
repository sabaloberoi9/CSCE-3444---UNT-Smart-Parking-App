"""API smoke tests. Skipped automatically if FastAPI isn't installed."""

from __future__ import annotations

import os
import tempfile
import unittest

try:
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover
    TestClient = None


@unittest.skipIf(TestClient is None, "fastapi not installed")
class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "api.db")
        import importlib

        import app.config
        import app.main

        importlib.reload(app.config)
        importlib.reload(app.main)
        cls.client_cm = TestClient(app.main.app)
        cls.client = cls.client_cm.__enter__()
        r = cls.client.post("/api/v1/auth/login", json={"email": "alex.commuter@demo.local", "password": "demo1234"})
        cls.headers = {"Authorization": f"Bearer {r.json()['token']}"}

    @classmethod
    def tearDownClass(cls):
        cls.client_cm.__exit__(None, None, None)

    def test_health_and_meta(self):
        self.assertEqual(self.client.get("/health").json(), {"status": "ok"})
        meta = self.client.get("/api/v1/meta").json()
        self.assertTrue(meta["demo_mode"])
        self.assertEqual(meta["milestone"], "60%")

    def test_campus_data(self):
        self.assertEqual(len(self.client.get("/api/v1/lots").json()), 12)
        self.assertEqual(len(self.client.get("/api/v1/buildings").json()), 16)
        self.assertIn("commuter", self.client.get("/api/v1/permit-types").json())

    def test_requires_login(self):
        self.assertEqual(self.client.get("/api/v1/me").status_code, 401)
        bad = {"Authorization": "Bearer not-a-token"}
        self.assertEqual(self.client.get("/api/v1/me", headers=bad).status_code, 401)

    def test_bad_login(self):
        r = self.client.post("/api/v1/auth/login", json={"email": "alex.commuter@demo.local", "password": "nope"})
        self.assertEqual(r.status_code, 401)

    def test_me_and_update(self):
        me = self.client.get("/api/v1/me", headers=self.headers).json()
        self.assertEqual(me["id"], "u_alex")
        r = self.client.patch("/api/v1/me", headers=self.headers, json={"accessible_routing": True})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["accessible_routing"])
        r = self.client.patch("/api/v1/me", headers=self.headers, json={"permit": "platinum"})
        self.assertEqual(r.status_code, 400)

    def test_register_flow(self):
        body = {"name": "New Student", "email": "new.student@demo.local", "password": "password123",
                "permit": "resident"}
        r = self.client.post("/api/v1/auth/register", json=body)
        self.assertEqual(r.status_code, 201)
        token = r.json()["token"]
        me = self.client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"}).json()
        self.assertEqual(me["permit"], "resident")
        self.assertEqual(self.client.post("/api/v1/auth/register", json=body).status_code, 409)
        short = {**body, "email": "other@demo.local", "password": "short"}
        self.assertEqual(self.client.post("/api/v1/auth/register", json=short).status_code, 422)

    def test_change_password_requires_login(self):
        r = self.client.post("/api/v1/auth/change-password",
                             json={"current_password": "demo1234", "new_password": "something9"})
        self.assertEqual(r.status_code, 401)


if __name__ == "__main__":
    unittest.main()
