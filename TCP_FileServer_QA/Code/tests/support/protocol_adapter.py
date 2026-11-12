"""Example wire protocol adapter (JSON + newline). Adjust to match project protocol.

Request examples:
 {"command":"PING"}
 {"command":"UPLOAD", "filename":"a.txt", "content_b64":"aGk="}
Response examples:
 {"status":"OK", ...}, {"status":"ERROR", "code":"FILE_EXISTS"}
"""
import base64
import json
import socket

MAX_LINE_BYTES = 8 * 1024 * 1024


def encode_request(command, **fields):
    return (json.dumps({"command": command, **fields}, ensure_ascii=False) + "\n").encode("utf-8")


def read_response(sock):
    buf = bytearray()
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Server closed connection before response")
        buf.extend(chunk)
        if len(buf) > MAX_LINE_BYTES:
            raise ValueError("Response exceeds maximum size")
        if b"\n" in buf:
            line, _, _ = buf.partition(b"\n")
            result = json.loads(line.decode("utf-8"))
            if not isinstance(result, dict):
                raise ValueError("Expected JSON object response")
            return result


def request(host, port, command, timeout=5.0, **fields):
    with socket.create_connection((host, port), timeout=timeout) as s:
        s.settimeout(timeout)
        s.sendall(encode_request(command, **fields))
        return read_response(s)


def upload(host, port, filename, payload, timeout=5.0):
    return request(host, port, "UPLOAD", timeout=timeout, filename=filename,
                   content_b64=base64.b64encode(payload).decode("ascii"))
