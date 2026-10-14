"""Service-level tests for the 60% milestone: database + seed data, authentication, profile, campus data.

Run from backend/:  python -m pytest  (or python -m unittest)
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.campus import BUILDINGS, LOTS
from app.config import Settings
from app.services.core import ParkingService, ServiceError
from app.services.security import decode_token, hash_password, verify_password

PASSWORD = "demo1234"


def make_service() -> ParkingService:
    s = Settings()
    s.db_path = Path(tempfile.mkdtemp()) / "test.db"
    return ParkingService(s, reset=True)


class DatabaseSeedTest(unittest.TestCase):  # TR-62, TR-63, TR-65
    def setUp(self):
        self.svc = make_service()

    def test_seed_counts(self):
        counts = self.svc.db.counts()
        self.assertEqual(counts["users"], 26)  # 6 demo accounts + 20 simulated background students
        self.assertEqual(counts["classes"], 9)
        self.assertEqual(counts["events"], 8)  # 6 game days, commencement, maintenance
        self.assertEqual(counts["favorites"], 4)
        for empty in ("saved_parking", "reports", "notifications", "lot_overrides", "audit_log"):
            self.assertEqual(counts[empty], 0, empty)

    def test_seed_is_idempotent(self):
        self.svc.db.seed(self.svc.settings.data_dir)
        self.assertEqual(self.svc.db.counts()["users"], 26)

    def test_reset_restores_seed(self):
        self.svc.register("Temp User", "temp@demo.local", "password123")
        self.assertEqual(self.svc.db.counts()["users"], 27)
        self.svc.db.reset_and_seed(self.svc.settings.data_dir)
        self.assertEqual(self.svc.db.counts()["users"], 26)

    def test_passwords_are_hashed(self):
        row = self.svc.db.one("SELECT password_hash FROM users WHERE id = 'u_alex'")
        self.assertTrue(row["password_hash"].startswith("pbkdf2$"))
        self.assertNotIn(PASSWORD, row["password_hash"])


class AuthTest(unittest.TestCase):  # FR-1
    def setUp(self):
        self.svc = make_service()

    def test_login_returns_token_for_user(self):
        out = self.svc.login("alex.commuter@demo.local", PASSWORD)
        self.assertEqual(out["user"]["permit"], "commuter")
        payload = decode_token(out["token"], self.svc.settings.jwt_secret)
        self.assertEqual(payload["sub"], "u_alex")

    def test_login_is_case_insensitive_on_email(self):
        self.assertEqual(self.svc.login("  Alex.Commuter@DEMO.local ", PASSWORD)["user"]["id"], "u_alex")

    def test_bad_password_rejected(self):
        with self.assertRaises(ServiceError) as cm:
            self.svc.login("alex.commuter@demo.local", "wrong")
        self.assertEqual(cm.exception.status, 401)

    def test_register_then_login(self):
        out = self.svc.register("Jamie Lee", "Jamie.Lee@my.unt.edu", "goMeanGreen1", "commuter")
        self.assertEqual(out["user"]["email"], "jamie.lee@my.unt.edu")
        self.assertEqual(out["user"]["role"], "student")
        self.assertEqual(self.svc.login("jamie.lee@my.unt.edu", "goMeanGreen1")["user"]["name"], "Jamie Lee")

    def test_register_validation(self):
        cases = [
            ("", "a@b.co", "password1", "none"),          # no name
            ("A", "not-an-email", "password1", "none"),   # bad email
            ("A", "a@b.co", "short", "none"),             # short password
            ("A", "a@b.co", "password1", "platinum"),     # unknown permit
        ]
        for args in cases:
            with self.assertRaises(ServiceError, msg=str(args)):
                self.svc.register(*args)

    def test_duplicate_email_conflict(self):
        with self.assertRaises(ServiceError) as cm:
            self.svc.register("Alex Again", "ALEX.commuter@demo.local", "password123")
        self.assertEqual(cm.exception.status, 409)

    def test_change_password(self):
        with self.assertRaises(ServiceError):
            self.svc.change_password("u_alex", "wrong", "newpassword1")
        self.svc.change_password("u_alex", PASSWORD, "newpassword1")
        with self.assertRaises(ServiceError):
            self.svc.login("alex.commuter@demo.local", PASSWORD)
        self.assertEqual(self.svc.login("alex.commuter@demo.local", "newpassword1")["user"]["id"], "u_alex")

    def test_hash_roundtrip(self):
        h = hash_password("abc12345")
        self.assertTrue(verify_password("abc12345", h))
        self.assertFalse(verify_password("abc12346", h))
        self.assertFalse(verify_password("abc12345", "garbage"))


class ProfileTest(unittest.TestCase):  # FR-15
    def setUp(self):
        self.svc = make_service()

    def test_public_user_hides_password(self):
        user = self.svc.public_user(self.svc.get_user("u_riley"))
        self.assertNotIn("password_hash", user)
        self.assertEqual(user["permit_label"], "Resident Student")
        self.assertEqual(user["home"]["label"], "Mean Green Village")

    def test_update_permit_name_home_and_prefs(self):
        out = self.svc.update_profile("u_alex", {
            "name": "Alex R.", "permit": "garage", "accessible_routing": True,
            "home": {"lat": 33.2, "lng": -97.13, "label": "New apartment"},
            "notifications": {"near_full": False, "quiet_start": "22:00", "quiet_end": "07:00"},
        })
        self.assertEqual(out["name"], "Alex R.")
        self.assertEqual(out["permit"], "garage")
        self.assertTrue(out["accessible_routing"])
        self.assertEqual(out["home"]["label"], "New apartment")
        self.assertFalse(out["notifications"]["near_full"])
        self.assertTrue(out["notifications"]["full"])  # untouched
        self.assertEqual(out["notifications"]["quiet_start"], "22:00")

    def test_clear_quiet_hours(self):
        self.svc.update_profile("u_alex", {"notifications": {"quiet_start": "22:00", "quiet_end": "07:00"}})
        out = self.svc.update_profile("u_alex", {"notifications": {"quiet_start": None, "quiet_end": ""}})
        self.assertIsNone(out["notifications"]["quiet_start"])
        self.assertIsNone(out["notifications"]["quiet_end"])

    def test_profile_validation(self):
        for bad in ({"permit": "platinum"}, {"notifications": {"quiet_start": "25:00"}}, {"name": "   "}):
            with self.assertRaises(ServiceError, msg=str(bad)):
                self.svc.update_profile("u_alex", bad)


class CampusDataTest(unittest.TestCase):  # FR-3, FR-4
    def setUp(self):
        self.svc = make_service()

    def test_buildings_and_lots(self):
        self.assertEqual(len(self.svc.buildings()), len(BUILDINGS))
        lots = self.svc.lots()
        self.assertEqual(len(lots), len(LOTS))
        for lot in lots:
            self.assertGreaterEqual(len(lot["polygon"]), 3)
            self.assertNotIn("rules", lot)

    def test_poi_filter(self):
        self.assertTrue(all(p["category"] == "dining" for p in self.svc.pois("dining")))
        with self.assertRaises(ServiceError):
            self.svc.pois("arcade")

    def test_events_seeded(self):
        events = self.svc.events()
        self.assertIsInstance(events[0]["lot_ids"], list)
        self.assertIn("maint_maple", {e["id"] for e in events})


if __name__ == "__main__":
    unittest.main()
