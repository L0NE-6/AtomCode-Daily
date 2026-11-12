import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from _loader import load_script


AC = load_script("atomcode_daily_readback", "atomcode_daily.py")


def plan_status(name="CodingPlan Lite", expires_at="2099-01-01T00:00:00Z", remaining=0):
    return {
        "codingplan_free": {
            "plan_name": name,
            "expires_at": expires_at,
            "remaining_days": remaining,
        },
        "rate_limit_windows": [],
    }


class FakeClient:
    name = "fixture"

    def __init__(self, statuses, claims):
        self.statuses = list(statuses)
        self.claims = list(claims)
        self.actions = []

    def status(self):
        self.actions.append("status")
        if not self.statuses:
            raise AssertionError("unexpected status request")
        value = self.statuses.pop(0)
        if isinstance(value, Exception):
            raise value
        return value

    def claim(self, tier):
        self.actions.append("claim:%s" % tier)
        if not self.claims:
            raise AssertionError("unexpected claim request: %s" % tier)
        return self.claims.pop(0)


class AtomCodeReadbackTests(unittest.TestCase):
    def test_claim_success_requires_status_v2_readback(self):
        client = FakeClient(
            statuses=[{}, plan_status("CodingPlan Max")],
            claims=[{"success": True, "message": "fixture granted"}],
        )

        ok, message = AC.run_account(client)

        self.assertTrue(ok)
        self.assertIn("状态回读确认", message)
        self.assertIn("Max 档", message)
        self.assertEqual(["status", "claim:Max", "status"], client.actions)

    def test_duplicate_claim_is_confirmed_by_active_plan_readback(self):
        client = FakeClient(
            statuses=[{}, plan_status("CodingPlan Pro", expires_at="", remaining=7)],
            claims=[{"duplicate": True, "message": "fixture duplicate"}],
        )

        ok, message = AC.run_account(client)

        self.assertTrue(ok)
        self.assertIn("已持有", message)
        self.assertIn("Pro 档", message)
        self.assertEqual(["status", "claim:Max", "status"], client.actions)

    def test_claim_receipt_without_status_readback_is_pending(self):
        client = FakeClient(
            statuses=[{}, AC.AtomCodeError("fixture status failed")],
            claims=[{"success": True, "message": "fixture granted"}],
        )

        ok, message = AC.run_account(client)

        self.assertFalse(ok)
        self.assertIn("待确认", message)
        self.assertIn("status-v2 回读失败", message)

    def test_status_readback_without_active_plan_is_not_success(self):
        client = FakeClient(
            statuses=[{}, {}],
            claims=[{"success": True, "message": "fixture granted"}],
        )

        ok, message = AC.run_account(client)

        self.assertFalse(ok)
        self.assertIn("未确认 Max/Pro/Lite", message)
        self.assertEqual(["status", "claim:Max", "status"], client.actions)

    def test_status_readback_requires_recognizable_tier(self):
        client = FakeClient(
            statuses=[{}, plan_status("CodingPlan Enterprise")],
            claims=[{"duplicate": True, "message": "fixture duplicate"}],
        )

        ok, message = AC.run_account(client)

        self.assertFalse(ok)
        self.assertIn("未确认 Max/Pro/Lite", message)

    def test_existing_active_plan_skips_claim(self):
        client = FakeClient(
            statuses=[plan_status("CodingPlan Lite")],
            claims=[],
        )

        ok, message = AC.run_account(client)

        self.assertTrue(ok)
        self.assertIn("Lite 档", message)
        self.assertEqual(["status"], client.actions)


if __name__ == "__main__":
    unittest.main()
