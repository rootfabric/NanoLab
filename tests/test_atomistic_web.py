"""Local HTTP integration tests. Runner fixtures do not perform physics."""
import copy
import http.client
import io
import json
import tempfile
import threading
import time
import unittest
import zipfile

from atomistic.web import DEFAULT_CONFIG, LocalApp, MAX_BODY, make_server
from atomistic.api import validate_config


def fixture_validator(config):
    if not isinstance(config, dict) or config != DEFAULT_CONFIG:
        raise ValueError("Only the explicit test configuration is supported")
    return copy.deepcopy(config)


def fixture_runner(config, output_root, run_id, **kwargs):
    """Intentionally synthetic, used only by these tests."""
    return {"status": "COMPLETED", "run_id": run_id,
            "trajectory": {"schema_version": "atomistic-trajectory-v1", "atom_count": 1,
                           "symbols": ["Cu"], "material": "Cu", "frames": [
                               {"step": 0, "time_fs": 0.0, "positions_angstrom": [[0, 0, 0]],
                                "potential_energy_ev": 0.1, "kinetic_energy_ev": 0.0,
                                "temperature_k": 0.0}]},
            "metrics": {"fixture": True}, "manifest": {"fixture": True}}


class LocalHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = LocalApp(self.temp.name, validator=fixture_validator, runner=fixture_runner)
        self.server = make_server(self.app, 0)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.app.stop()
        if self.app.worker:
            self.app.worker.join(2)
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(2)
        self.temp.cleanup()

    def request(self, method="GET", path="/api/state", payload=None, headers=None, raw=None):
        body = json.dumps(payload).encode() if payload is not None else raw
        full_headers = {"Host": f"127.0.0.1:{self.port}"}
        if method == "POST":
            full_headers.update({"Content-Type": "application/json", "X-NanoLab-Token": self.app.token})
        full_headers.update(headers or {})
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        conn.request(method, path, body=body, headers=full_headers)
        response = conn.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        conn.close()
        return result

    def completed_run(self):
        status, _, _ = self.request("POST", "/api/run", DEFAULT_CONFIG)
        self.assertEqual(status, 202)
        self.app.worker.join(2)
        self.assertFalse(self.app.worker.is_alive())

    def test_empty_state_and_static_security_headers(self):
        status, headers, data = self.request()
        self.assertEqual(status, 200)
        state = json.loads(data)
        self.assertIsNone(state["job"])
        self.assertEqual(state["token"], self.app.token)
        status, headers, data = self.request(path="/")
        self.assertEqual(status, 200)
        self.assertIn("Инженерная демонстрация".encode(), data)
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertEqual(headers["Cross-Origin-Resource-Policy"], "same-origin")
        self.assertNotIn("Access-Control-Allow-Origin", headers)

    def test_full_fixture_calculation_and_export(self):
        self.completed_run()
        self.assertEqual(self.app.snapshot()["job"]["status"], "completed")
        status, _, data = self.request(path="/api/trajectory")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(data)["atom_count"], 1)
        status, headers, data = self.request(path="/api/export.zip")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/zip")
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            self.assertEqual(set(archive.namelist()), {"config.json", "trajectory.json", "metrics.json", "manifest.json"})
            self.assertEqual(json.loads(archive.read("config.json")), DEFAULT_CONFIG)
            self.assertTrue(json.loads(archive.read("manifest.json"))["fixture"])

    def test_result_is_not_fabricated_before_run(self):
        for path in ("/api/trajectory", "/api/export.zip"):
            self.assertEqual(self.request(path=path)[0], 409)

    def test_refuse_external_host_origin_and_missing_token(self):
        self.assertEqual(self.request(headers={"Host": "evil.example"})[0], 403)
        self.assertEqual(self.request(headers={"Origin": "https://evil.example"})[0], 403)
        self.assertEqual(self.request("POST", "/api/run", DEFAULT_CONFIG, {"X-NanoLab-Token": ""})[0], 403)
        self.assertEqual(self.request("POST", "/api/run", DEFAULT_CONFIG, {"Origin": "http://evil.example"})[0], 403)
        self.assertEqual(self.app.runs_started, 0)

    def test_no_arbitrary_files_or_paths(self):
        for path in ("/../AGENTS.md", "/%2e%2e/AGENTS.md", "/static/../../etc/passwd", "/api/config?path=/etc/passwd", "/app.js?file=/etc/passwd"):
            self.assertEqual(self.request(path=path)[0], 404)

    def test_reject_bad_json_nonfinite_and_wrong_type(self):
        for body in (b"bad json", b'{"x":NaN}', b'{"x":1,"x":2}', b"[]", b"null", b'"/etc/passwd"'):
            self.assertEqual(self.request("POST", "/api/run", raw=body)[0], 400)
        self.assertEqual(self.app.runs_started, 0)

    def test_request_size_and_content_type_limit(self):
        self.assertEqual(self.request("POST", "/api/run", raw=b" " * (MAX_BODY+1))[0], 413)
        self.assertEqual(self.request("POST", "/api/run", DEFAULT_CONFIG, {"Content-Type": "text/plain"})[0], 415)
        self.assertEqual(self.app.runs_started, 0)

    def test_validation_precedes_worker_and_budget(self):
        invalid = copy.deepcopy(DEFAULT_CONFIG)
        invalid["structure"]["size"] = [1000, 1, 1]
        self.assertEqual(self.request("POST", "/api/run", invalid)[0], 400)
        self.assertIsNone(self.app.worker)
        self.assertEqual(self.app.runs_started, 0)

    def test_real_backend_validation_blocks_units_material_caps_and_paths(self):
        self.app.validator = validate_config
        self.assertEqual(validate_config(DEFAULT_CONFIG), DEFAULT_CONFIG)
        variants = []
        for section, key, value in (("structure", "size", [16, 16, 16]),
                                    ("md", "steps", 2001), ("md", "sample_interval", 0),
                                    ("md", "timestep_fs", 1000), ("md", "temperature_k", 10000)):
            invalid = copy.deepcopy(DEFAULT_CONFIG)
            invalid[section][key] = value
            variants.append(invalid)
        for key, value in (("material", "Fe"), ("output_root", "/etc"),
                           ("run_id", "$(touch injected)")):
            invalid = copy.deepcopy(DEFAULT_CONFIG)
            invalid[key] = value
            variants.append(invalid)
        for invalid in variants:
            self.assertEqual(self.request("POST", "/api/run", invalid)[0], 400)
        self.assertEqual(self.app.runs_started, 0)

    def test_single_job_and_cancellation(self):
        started = threading.Event()
        def blocking_runner(config, root, run_id, *, cancel_event, **kwargs):
            started.set()
            if not cancel_event.wait(2):
                raise RuntimeError("Fixture cancellation timeout")
            raise RuntimeError("Cancelled fixture")
        self.app.runner = blocking_runner
        self.assertEqual(self.request("POST", "/api/run", DEFAULT_CONFIG)[0], 202)
        self.assertTrue(started.wait(1))
        self.assertEqual(self.request("POST", "/api/run", DEFAULT_CONFIG)[0], 409)
        self.assertEqual(self.request("POST", "/api/stop", {})[0], 202)
        self.app.worker.join(2)
        self.assertEqual(self.app.snapshot()["job"]["status"], "cancelled")
        self.assertEqual(self.app.runs_started, 1)

    def test_failed_runner_does_not_get_silent_retry_or_results(self):
        def broken(*args, **kwargs):
            raise RuntimeError("Known fixture failure")
        self.app.runner = broken
        self.completed_run()
        snapshot = self.app.snapshot()
        self.assertEqual(snapshot["job"]["status"], "failed")
        self.assertEqual(snapshot["job"]["error"], "Known fixture failure")
        self.assertEqual(snapshot["runs_started"], 1)
        self.assertEqual(self.request(path="/api/trajectory")[0], 409)

    def test_session_budget_refuses_ninth_job_or_time_overrun(self):
        self.app.runs_started = 8
        self.assertEqual(self.request("POST", "/api/run", DEFAULT_CONFIG)[0], 409)
        self.app.runs_started = 0
        self.app.compute_seconds = 1200
        self.assertEqual(self.request("POST", "/api/run", DEFAULT_CONFIG)[0], 409)

    def test_loopback_binding(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")


if __name__ == "__main__":
    unittest.main()
