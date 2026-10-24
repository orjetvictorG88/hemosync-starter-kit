import asyncio
import importlib
import os
import sys
import tempfile
import unittest

from starlette.requests import Request
from starlette.responses import Response

_database_directory = tempfile.TemporaryDirectory()
_previous_database_path = os.environ.get("HEMOSYNC_DB_PATH")
os.environ["HEMOSYNC_DB_PATH"] = os.path.join(_database_directory.name, "hemosync.sqlite3")
api = importlib.reload(sys.modules["api"]) if "api" in sys.modules else importlib.import_module("api")

if _previous_database_path is None:
    os.environ.pop("HEMOSYNC_DB_PATH", None)
else:
    os.environ["HEMOSYNC_DB_PATH"] = _previous_database_path


class TestLoopbackOnlyAPI(unittest.TestCase):
    def _request(self, host, request_host="127.0.0.1:8000", method="GET", origin=None):
        headers = [(b"host", request_host.encode())]
        if origin is not None:
            headers.append((b"origin", origin.encode()))
        return Request({
            "type": "http",
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": "/health",
            "raw_path": b"/health",
            "query_string": b"",
            "headers": headers,
            "client": (host, 12345),
            "server": ("127.0.0.1", 8000),
        })

    def test_remote_clients_are_denied_before_the_endpoint_runs(self):
        endpoint_called = False

        async def call_next(_request):
            nonlocal endpoint_called
            endpoint_called = True
            return Response(status_code=200)

        response = asyncio.run(api.restrict_to_loopback(self._request("203.0.113.20"), call_next))

        self.assertEqual(response.status_code, 403)
        self.assertFalse(endpoint_called)

    def test_loopback_clients_are_allowed(self):
        async def call_next(_request):
            return Response(status_code=200)

        response = asyncio.run(api.restrict_to_loopback(self._request("127.0.0.1"), call_next))

        self.assertEqual(response.status_code, 200)

    def test_external_host_header_is_denied_for_loopback_clients(self):
        async def call_next(_request):
            self.fail("Endpoint must not run for an external Host header")

        response = asyncio.run(
            api.restrict_to_loopback(
                self._request("127.0.0.1", request_host="attacker.example"),
                call_next,
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_cross_origin_browser_writes_are_denied(self):
        async def call_next(_request):
            self.fail("Endpoint must not run for a cross-origin write")

        response = asyncio.run(
            api.restrict_to_loopback(
                self._request(
                    "127.0.0.1",
                    method="POST",
                    origin="http://attacker.example",
                ),
                call_next,
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_same_origin_browser_writes_are_allowed(self):
        async def call_next(_request):
            return Response(status_code=200)

        response = asyncio.run(
            api.restrict_to_loopback(
                self._request(
                    "127.0.0.1",
                    method="POST",
                    origin="http://127.0.0.1:8000",
                ),
                call_next,
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_mismatched_origin_port_is_denied(self):
        async def call_next(_request):
            self.fail("Endpoint must not run for an origin on another port")

        response = asyncio.run(
            api.restrict_to_loopback(
                self._request(
                    "127.0.0.1",
                    method="POST",
                    origin="http://127.0.0.1:8001",
                ),
                call_next,
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_non_ip_client_values_are_denied(self):
        self.assertFalse(api.is_loopback_client("localhost"))
        self.assertFalse(api.is_loopback_client(None))

    def test_demo_encounters_are_explicitly_synthetic_and_include_chart_groups(self):
        response = api.demo_encounters()

        self.assertTrue(response["synthetic"])
        self.assertEqual(len(response["encounters"]), 5)
        self.assertEqual(response["encounters"][0], {"id": "P-7788", "bed": 1, "blood_group": "O+"})
        groups = {"O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"}
        self.assertTrue(all(encounter["blood_group"] in groups for encounter in response["encounters"]))

    def test_demo_seed_spreads_expiry_dates_and_remains_idempotent(self):
        first = api.reset_demo()
        first_expiries = {
            unit.din: unit.expires
            for unit in api.BANKS["API-SITE"].units.values()
        }
        second = api.reset_demo()

        self.assertFalse(first["already_loaded"])
        self.assertTrue(second["already_loaded"])
        self.assertEqual(len(set(first_expiries.values())), 7)
        self.assertEqual(
            first_expiries,
            {unit.din: unit.expires for unit in api.BANKS["API-SITE"].units.values()},
        )


def tearDownModule():
    _database_directory.cleanup()


if __name__ == "__main__":
    unittest.main()
