"""TCP QA: protocol, concurrency, dropped connection, duplicate filename.

Run against reference mock by default; set QA_HOST and QA_PORT to test actual server.
Adapter in support/protocol_adapter.py MUST match real server's protocol first.
"""
import concurrent.futures
import os
import socket
import unittest
import uuid

from .support.mock_server import MockTCPServer
from .support.protocol_adapter import encode_request, request, upload


class TCPQATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        host = os.getenv("QA_HOST")
        port = os.getenv("QA_PORT")
        if bool(host) != bool(port):
            raise ValueError("Set both QA_HOST and QA_PORT, or neither")
        cls.mock = None
        if host:
            cls.host, cls.port = host, int(port)
            cls.target = "REAL SERVER (adapter must match application protocol)"
        else:
            cls.mock = MockTCPServer().start()
            cls.host, cls.port = cls.mock.server_address
            cls.target = "REFERENCE MOCK (not evidence about real server)"
        print("\nQA target:", cls.target, cls.host, cls.port)

    @classmethod
    def tearDownClass(cls):
        if cls.mock:
            cls.mock.stop()

    def unique_name(self, suffix=".bin"):
        return "qa_" + uuid.uuid4().hex + suffix

    def test_01_tcp_connect_and_protocol_ping(self):
        # TC-01: valid TCP connect and expected PING/PONG response.
        result = request(self.host, self.port, "PING")
        self.assertEqual(result.get("status"), "OK")
        self.assertEqual(result.get("message"), "PONG")

    def test_02_upload_large_file(self):
        # TC-02: transfer 1 MiB; use checksums/GET in the real app if available.
        payload = os.urandom(1024 * 1024)
        result = upload(self.host, self.port, self.unique_name(), payload, timeout=15)
        self.assertEqual(result.get("status"), "OK")
        self.assertEqual(result.get("bytes"), len(payload))
        if self.mock:
            self.assertIn(payload, self.mock.files.values())

    def test_03_concurrent_uploads(self):
        # TC-03: simulate 10 simultaneous clients with distinct target filenames.
        jobs = [(self.unique_name(), os.urandom(4096)) for _ in range(10)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(upload, self.host, self.port, name, data, 15) for name, data in jobs]
            results = [f.result(timeout=20) for f in futures]
        self.assertTrue(all(r.get("status") == "OK" for r in results), results)
        if self.mock:
            for name, payload in jobs:
                self.assertEqual(self.mock.files[name], payload)

    def test_04_network_cut_mid_request(self):
        # TC-04: disconnect while sending incomplete request; server must remain usable.
        with socket.create_connection((self.host, self.port), timeout=5) as s:
            s.sendall(encode_request("UPLOAD", filename=self.unique_name(), content_b64="Zm9v")[:-5])
            # Socket closed before newline / complete request.
        result = request(self.host, self.port, "PING", timeout=5)
        self.assertEqual(result.get("status"), "OK", "Server stopped responding after abrupt disconnect")

    def test_05_duplicate_filename(self):
        # TC-05: reference policy = reject duplicate, do not overwrite the first file.
        name = self.unique_name()
        first = upload(self.host, self.port, name, b"original")
        second = upload(self.host, self.port, name, b"different")
        self.assertEqual(first.get("status"), "OK")
        self.assertEqual(second.get("status"), "ERROR")
        self.assertEqual(second.get("code"), "FILE_EXISTS")
        if self.mock:
            self.assertEqual(self.mock.files[name], b"original")

    def test_06_unknown_command(self):
        # TC-06: reject invalid/unknown protocol command.
        result = request(self.host, self.port, "INVALID_QA_COMMAND")
        self.assertEqual(result.get("status"), "ERROR")


if __name__ == "__main__":
    unittest.main()
