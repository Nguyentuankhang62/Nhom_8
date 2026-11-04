"""Core TCP server implementation for the UDM_11 project."""

from __future__ import annotations

import socket
import threading
from pathlib import Path
from typing import Optional

from Code.server.file_service import FileService
from Code.server.protocol import MessageProtocol


class TCPServer:
    """A multithreaded TCP server that supports LIST_FILES and DOWNLOAD commands."""

    CHUNK_SIZE = 4096

    def __init__(self, host: str = "0.0.0.0", port: int = 5000, shared_dir: str | Path = "./shared_files"):
        self.host = host
        self.port = port
        self.file_service = FileService(shared_dir)
        self.protocol = MessageProtocol()
        self._stop_event = threading.Event()
        self._server_socket: Optional[socket.socket] = None

    def start(self) -> None:
        """Start accepting incoming client connections."""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(10)

        print(f"TCP server is listening on {self.host}:{self.port}")

        while not self._stop_event.is_set():
            try:
                client_socket, client_address = self._server_socket.accept()
            except OSError:
                if self._stop_event.is_set():
                    break
                continue

            thread = threading.Thread(
                target=self._handle_client,
                args=(client_socket, client_address),
                daemon=True,
            )
            thread.start()

    def stop(self) -> None:
        """Stop the server gracefully."""
        self._stop_event.set()
        if self._server_socket is not None:
            try:
                self._server_socket.close()
            except OSError:
                pass

    def _handle_client(self, client_socket: socket.socket, client_address: tuple[str, int]) -> None:
        """Handle one connection from a single client in its own thread."""
        print(f"[Client {client_address}] connected")
        buffered_data = ""

        try:
            while not self._stop_event.is_set():
                data = client_socket.recv(self.CHUNK_SIZE)
                if not data:
                    break

                buffered_data += self.protocol.parse_command(data)

                while "\n" in buffered_data:
                    line, buffered_data = buffered_data.split("\n", 1)
                    if not line:
                        continue
                    self._process_command(client_socket, line.strip())

        except (ConnectionError, OSError) as exc:
            print(f"[Client {client_address}] connection error: {exc}")
        finally:
            client_socket.close()
            print(f"[Client {client_address}] disconnected")

    def _process_command(self, client_socket: socket.socket, command: str) -> None:
        """Execute a single client command and return the server response."""
        command = command.strip()
        if not command:
            return

        if command == "LIST_FILES":
            file_names = self.file_service.list_files()
            response = self.protocol.build_file_list_response(file_names)
            client_socket.sendall(response)
            return

        if command.startswith("DOWNLOAD|"):
            file_name = command.split("|", 1)[1].strip()
            if not file_name:
                client_socket.sendall(self.protocol.build_error_response())
                return

            try:
                file_path = self.file_service.get_file_path(file_name)
            except FileNotFoundError:
                client_socket.sendall(self.protocol.build_error_response())
                return

            file_size = file_path.stat().st_size
            client_socket.sendall(self.protocol.build_file_info_response(file_path.name, file_size))

            with file_path.open("rb") as file_handle:
                while True:
                    chunk = file_handle.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
            return

        client_socket.sendall(self.protocol.build_error_response("Lệnh không hợp lệ"))
