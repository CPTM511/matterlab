from __future__ import annotations

import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


class EvidenceHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if urlsplit(self.path).path == "/":
            self.send_response(302)
            self.send_header("Location", "/ui/index.html")
            self.end_headers()
            return
        path = unquote(urlsplit(self.path).path).lstrip("/")
        root = Path(self.directory).resolve()
        actual = (root / path).resolve()
        allowed = path.split("/", 1)[0] in {"ui", "runs", "docs"}
        if not allowed or not actual.is_relative_to(root) or not actual.is_file() or any(x.startswith(".") for x in Path(path).parts):
            self.send_error(404)
            return
        super().do_GET()

    def do_HEAD(self):
        # Use the same path restrictions; no arbitrary project directory listing.
        self.send_error(405)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(prog="matterlab", description="Free local material generation and evidence browser; no API required")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("generate", "run"):
        p = sub.add_parser(name)
        p.add_argument("--config", default="configs/round-001.json")
        p.add_argument("--output", default="runs/round-001")
        if name == "run":
            p.add_argument("--resume", action="store_true")
    for name in ("verify", "report"):
        p = sub.add_parser(name)
        p.add_argument("directory")
    p = sub.add_parser("serve")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--root", default=".")
    args = parser.parse_args()
    if args.command == "generate":
        from .generate import generate
        output = Path(args.output)
        if output.exists():
            parser.error("Output exists. Choose a new directory to preserve evidence.")
        result = generate(json.loads(Path(args.config).read_text()), output / "generated")
        print(json.dumps(result["groups"], indent=2))
    elif args.command == "run":
        from .simulate import run
        from .report import report
        from .evidence import manifest, verify
        run(args.config, args.output, args.resume)
        report(args.output)
        manifest(args.output)
        result = verify(args.output)
        print(json.dumps(result, indent=2))
        if not result["passed"]:
            raise SystemExit(1)
    elif args.command == "verify":
        from .evidence import verify
        result = verify(args.directory)
        print(json.dumps(result, indent=2))
        if not result["passed"]:
            raise SystemExit(1)
    elif args.command == "report":
        from .report import report
        from .evidence import manifest
        report(args.directory)
        manifest(args.directory)
    else:
        handler = partial(EvidenceHandler, directory=str(Path(args.root).resolve()))
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
        print(f"MatterLab: http://127.0.0.1:{args.port}/ (read-only, local only)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()


if __name__ == "__main__":
    main()
