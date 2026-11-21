"""Serve the token warehouse and testnet factory on localhost."""
import argparse
import csv
import json
from decimal import DecimalException
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from token_inventory import load_inventory
from token_plan import PlanError, build_plan

WEB = Path(__file__).resolve().parents[1] / "web"
FILES = {
    "/": ("index.html", "text/html"),
    "/app.js": ("app.js", "text/javascript"),
    "/style.css": ("style.css", "text/css"),
}


class AppHandler(BaseHTTPRequestHandler):
    def respond(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def respond_json(self, status, data):
        self.respond(status, "application/json", json.dumps(data).encode())

    def do_GET(self):
        if self.path == "/api/inventory":
            try:
                tokens = load_inventory()
            except (OSError, ValueError, csv.Error):
                self.respond_json(500, {"error": "The warehouse inventory could not be loaded."})
                return
            self.respond_json(200, tokens)
            return
        if self.path in FILES:
            filename, content_type = FILES[self.path]
            self.respond(200, content_type, (WEB / filename).read_bytes())
            return
        self.send_error(404)

    def do_POST(self):
        if self.path != "/api/plan":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 16384:
                raise ValueError
            config = json.loads(self.rfile.read(length))
            if not isinstance(config, dict):
                raise ValueError
            lines = build_plan(config)
        except PlanError as exc:
            self.respond_json(400, {"error": str(exc)})
            return
        except DecimalException:
            self.respond_json(400, {"error": "Supply is outside the supported decimal range."})
            return
        except ValueError:
            self.respond_json(400, {"error": "Expected a JSON configuration object of up to 16 KiB."})
            return
        try:
            matches = [
                token for token in load_inventory()
                if token["symbol"] == config["symbol"]
            ]
        except (OSError, ValueError, csv.Error):
            self.respond_json(500, {"error": "The warehouse inventory could not be checked."})
            return
        self.respond_json(200, {"plan": "\n".join(lines), "inventory_matches": matches})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), AppHandler) as server:
        print(f"Open http://127.0.0.1:{server.server_port}", flush=True)
        server.serve_forever()
