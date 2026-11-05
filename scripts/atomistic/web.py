"""Loopback-only local UI. No scientific calculation is performed on import."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import io
import json
import secrets
import threading
import time
import uuid
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MAX_BODY = 16_384
EXPORT_FILES = frozenset({"config.json", "protocol.json", "worker.log", "metrics.json",
                          "trajectory.json", "report.md", "environment.json",
                          "numerical-control.json", "relaxation.json", "relaxation.log"})
STATIC = Path(__file__).with_name("static")
DEFAULT_CONFIG = {
    "schema_version": "atomistic-config-v1",
    "material": "Cu", "model": "ASE_EMT_Cu",
    "structure": {"kind": "fcc_cuboid", "size": [2, 2, 2], "lattice_constant_angstrom": 3.61},
    "relaxation": {"max_steps": 100, "fmax_ev_per_angstrom": 0.05},
    "md": {"steps": 50, "timestep_fs": 1, "temperature_k": 100,
           "friction_per_fs": 0.01, "sample_interval": 5, "seed": 1729},
}


class BusyError(ValueError):
    pass


class LocalApp:
    """One active job, bounded session budget, explicit cancellation."""

    def __init__(self, output_root, *, validator=None, runner=None):
        if validator is None or runner is None:
            from .api import run, validate_config
            validator, runner = validate_config, run
        self.validator, self.runner = validator, runner
        # Preserve suspicious components for the backend's path validation.
        self.output_root = Path(output_root).absolute()
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.Lock()
        self.cancel_event = threading.Event()
        self.worker = None
        self.job = None
        self.result = None
        self.runs_started = 0
        self.compute_seconds = 0.0

    def snapshot(self):
        with self.lock:
            job = dict(self.job) if self.job else None
            if job and job["status"] in ("running", "stopping"):
                job["elapsed_seconds"] = round(time.monotonic() - job["started_monotonic"], 1)
            if job:
                job.pop("started_monotonic", None)
            return {"job": job, "runs_started": self.runs_started,
                    "max_runs": 8, "compute_seconds": round(self.compute_seconds, 2),
                    "claim": "SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED"}

    def start(self, config):
        validated = self.validator(config)
        with self.lock:
            if self.job and self.job["status"] in ("running", "stopping"):
                raise BusyError("Уже выполняется расчёт. Дождитесь завершения или остановите его.")
            if self.runs_started >= 8 or self.compute_seconds >= 1200:
                raise BusyError("Исчерпан бюджет этой сессии: 8 запусков / 20 минут.")
            # Backend enforces per-run timeout; keep the cumulative session cap too.
            timeout = max(1, min(120, int(1200 - self.compute_seconds)))
            run_id = "ui-" + uuid.uuid4().hex
            self.cancel_event = threading.Event()
            self.runs_started += 1
            self.result = None
            self.job = {"run_id": run_id, "status": "running", "config": validated,
                        "started_monotonic": time.monotonic(), "timeout_seconds": timeout}
            self.worker = threading.Thread(target=self._execute, args=(validated, run_id, timeout), daemon=True)
            self.worker.start()
        return run_id

    def _execute(self, config, run_id, timeout):
        try:
            result = self.runner(config, self.output_root, run_id,
                                 timeout_seconds=timeout, cancel_event=self.cancel_event)
            with self.lock:
                self.result = result
                outcome = str(result.get("status", "COMPLETED")).upper()
                self.job["status"] = "completed" if outcome == "COMPLETED" else outcome.lower()
        except Exception as exc:
            with self.lock:
                self.job["status"] = "cancelled" if self.cancel_event.is_set() else "failed"
                self.job["error"] = str(exc)[:1000]
        finally:
            with self.lock:
                elapsed = time.monotonic() - self.job["started_monotonic"]
                self.job["elapsed_seconds"] = round(elapsed, 2)
                self.compute_seconds += elapsed

    def stop(self):
        with self.lock:
            if self.job and self.job["status"] in ("running", "stopping"):
                self.job["status"] = "stopping"
                self.cancel_event.set()

    def artifact(self, name):
        with self.lock:
            return self._artifact_locked(name)

    def _artifact_locked(self, name):
        if not self.job:
            raise ValueError("Расчётов ещё нет.")
        if name == "config":
            return self.job["config"]
        if self.job["status"] != "completed" or self.result is None:
            raise ValueError("Результат ещё не готов.")
        if name not in ("trajectory", "metrics", "manifest"):
            raise ValueError("Неизвестный артефакт.")
        return self.result[name]

    def export(self):
        # Only the server-generated run directory is eligible. Serve the exact
        # original bytes, so the downloaded manifest remains verifiable.
        with self.lock:
            self._artifact_locked("manifest")
            run_dir = self.output_root / self.job["run_id"]
            if Path(self.result.get("run_dir", "")).absolute() != run_dir:
                raise ValueError("Путь результата не совпадает с каталогом расчёта.")
            if ".." in run_dir.parts or any(p.is_symlink() for p in [run_dir, *run_dir.parents]):
                raise ValueError("Небезопасный каталог результата.")
            manifest_path = run_dir / "manifest.json"
            if manifest_path.is_symlink() or manifest_path.stat().st_size > 65536:
                raise ValueError("Небезопасный manifest результата.")
            manifest_bytes = manifest_path.read_bytes()
            manifest = json.loads(manifest_bytes)
            from .api import CLAIM, MAX_OUTPUT_BYTES
            if (manifest.get("schema_version") != "atomistic-manifest-v1"
                    or manifest.get("status") != "COMPLETED"
                    or manifest.get("run_id") != self.job["run_id"]
                    or manifest.get("claim_ceiling") != CLAIM
                    or manifest != self.result["manifest"]):
                raise ValueError("Manifest результата изменён или некорректен.")
            declared = manifest.get("files")
            if not isinstance(declared, dict) or set(declared) != EXPORT_FILES:
                raise ValueError("Неполный или неизвестный состав результата.")
            files = {"manifest.json": manifest_bytes}
            total = len(manifest_bytes)
            for name, expected in declared.items():
                target = run_dir / name
                if target.is_symlink() or not target.is_file():
                    raise ValueError("Небезопасный артефакт результата: " + name)
                total += target.stat().st_size
                if total > MAX_OUTPUT_BYTES + 65536:
                    raise ValueError("Превышен предел размера результата.")
                data = target.read_bytes()
                if expected != {"sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data)}:
                    raise ValueError("Нарушена целостность результата: " + name)
                files[name] = data
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, data in files.items():
                archive.writestr(name, data)
        return payload.getvalue()


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2).encode("utf-8")


def make_server(app, port=8765):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _send(self, code, data, mime="application/json; charset=utf-8", attachment=None):
            self.send_response(code)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' blob:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            if attachment:
                self.send_header("Content-Disposition", f'attachment; filename="{attachment}"')
            self.end_headers()
            self.wfile.write(data)

        def _json(self, code, value):
            self._send(code, json_bytes(value))

        def _trusted(self):
            port = self.server.server_address[1]
            hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
            host = self.headers.get("Host", "")
            if host not in hosts:
                self._json(403, {"error": "Разрешён только loopback Host."})
                return False
            origin = self.headers.get("Origin")
            if origin is not None and origin != "http://" + host:
                self._json(403, {"error": "Запрещён внешний Origin."})
                return False
            return True

        def do_GET(self):
            if not self._trusted():
                return
            path = self.path
            static = {"/": ("index.html", "text/html; charset=utf-8"),
                      "/app.js": ("app.js", "application/javascript; charset=utf-8"),
                      "/style.css": ("style.css", "text/css; charset=utf-8")}
            if path in static:
                name, mime = static[path]
                self._send(200, (STATIC / name).read_bytes(), mime)
            elif path == "/api/state":
                self._json(200, {**app.snapshot(), "token": app.token, "defaults": DEFAULT_CONFIG})
            elif path in ("/api/trajectory", "/api/metrics", "/api/manifest", "/api/config"):
                try:
                    self._json(200, app.artifact(path.rsplit("/", 1)[1]))
                except (ValueError, KeyError, OSError) as exc:
                    self._json(409, {"error": str(exc)})
            elif path == "/api/export.zip":
                try:
                    self._send(200, app.export(), "application/zip", "nanolab-result.zip")
                except (ValueError, KeyError, OSError) as exc:
                    self._json(409, {"error": str(exc)})
            else:
                self._json(404, {"error": "Не найдено."})

        def do_POST(self):
            if not self._trusted():
                return
            if not hmac.compare_digest(self.headers.get("X-NanoLab-Token", ""), app.token):
                self._json(403, {"error": "Неверный токен сессии."})
                return
            if self.headers.get("Transfer-Encoding"):
                self._json(400, {"error": "Transfer-Encoding не поддерживается."})
                return
            try:
                length = int(self.headers.get("Content-Length", "-1"))
            except ValueError:
                length = -1
            if not 0 <= length <= MAX_BODY:
                self._json(413, {"error": "Недопустимый размер запроса."})
                return
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip() != "application/json":
                self._json(415, {"error": "Требуется application/json."})
                return
            self.connection.settimeout(5)
            try:
                raw = self.rfile.read(length)
                if len(raw) != length:
                    raise ValueError("Неполное тело запроса.")
                def unique_keys(pairs):
                    result = {}
                    for key, value in pairs:
                        if key in result:
                            raise ValueError("Повтор ключа JSON: " + key)
                        result[key] = value
                    return result
                payload = json.loads(raw, object_pairs_hook=unique_keys,
                                     parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Число должно быть конечным.")))
                if self.path == "/api/run":
                    self._json(202, {"run_id": app.start(payload)})
                elif self.path == "/api/stop":
                    app.stop()
                    self._json(202, {"status": "stop_requested"})
                else:
                    self._json(404, {"error": "Не найдено."})
            except BusyError as exc:
                self._json(409, {"error": str(exc)})
            except (ValueError, TypeError, UnicodeError, TimeoutError) as exc:
                self._json(400, {"error": str(exc)[:1000]})

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    return server


def main(argv=None):
    parser = argparse.ArgumentParser(description="Локальный NanoLab: Cu / ASE EMT (инженерная демонстрация)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--output-root", type=Path, default=Path("atomistic-runs"))
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error("port must be in 0..65535")
    app = LocalApp(args.output_root)
    server = make_server(app, args.port)
    print(f"NanoLab: http://127.0.0.1:{server.server_address[1]} (Ctrl+C — остановить)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        app.stop()
        if app.worker:
            app.worker.join(timeout=8)
        server.server_close()


if __name__ == "__main__":
    main()
