"""Reference mock server. It is NOT the project's actual server."""
import base64
import json
import socketserver
import threading


class _Handler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            line = self.rfile.readline(8 * 1024 * 1024 + 1)
            if not line or len(line) > 8 * 1024 * 1024:
                return
            data = json.loads(line.decode("utf-8"))
            if data.get("command") == "PING":
                reply = {"status": "OK", "message": "PONG"}
            elif data.get("command") == "UPLOAD":
                filename = data.get("filename", "")
                content = base64.b64decode(data.get("content_b64", ""), validate=True)
                if not filename or filename in (".", "..") or "/" in filename or "\\" in filename:
                    reply = {"status": "ERROR", "code": "INVALID_FILENAME"}
                else:
                    with self.server.files_lock:
                        if filename in self.server.files:
                            reply = {"status": "ERROR", "code": "FILE_EXISTS"}
                        else:
                            self.server.files[filename] = content
                            reply = {"status": "OK", "bytes": len(content)}
            else:
                reply = {"status": "ERROR", "code": "UNKNOWN_COMMAND"}
            self.wfile.write((json.dumps(reply) + "\n").encode("utf-8"))
        except (ValueError, KeyError, TypeError, OSError):
            pass  # A dropped or malformed connection is isolated to its handler.


class MockTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self):
        super().__init__(("127.0.0.1", 0), _Handler)
        self.files = {}
        self.files_lock = threading.Lock()
        self.worker = threading.Thread(target=self.serve_forever, daemon=True)

    def start(self):
        self.worker.start()
        return self

    def stop(self):
        self.shutdown()
        self.server_close()
        self.worker.join(timeout=3)
