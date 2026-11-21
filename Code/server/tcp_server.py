"""Core TCP server implementation for the UDM_11 project."""

from __future__ import annotations

import socket
import sys
import threading
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Code.server.file_service import FileService
from Code.server.protocol import MessageProtocol
from Code.utils.logger import get_logger


class TCPServer:
    """A multithreaded TCP server that supports LIST_FILES and DOWNLOAD commands."""

    CHUNK_SIZE = 4096

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 5000,
        shared_dir: str | Path = "./shared_files",
    ):
        self.host = host
        self.port = port
        self.file_service = FileService(shared_dir)
        self.protocol = MessageProtocol()
        self.logger = get_logger("UDM_11.Server")
        self._stop_event = threading.Event()
        self._server_socket: Optional[socket.socket] = None

    def start(self) -> None:
        """Start accepting incoming client connections."""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(10)

        self.logger.info("TCP server is listening on %s:%s", self.host, self.port)

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
        self.logger.info("TCP server stopped")

    def _handle_client(
        self, client_socket: socket.socket, client_address: tuple[str, int]
    ) -> None:
        """Handle one connection from a single client in its own thread."""
        self.logger.info("[Client %s] connected", client_address)
        buffered_data = ""

        try:
            client_socket.settimeout(30)
            while not self._stop_event.is_set():
                data = client_socket.recv(self.CHUNK_SIZE)
                if not data:
                    break

                buffered_data += self.protocol.parse_command(data)

                while "\n" in buffered_data:
                    line, buffered_data = buffered_data.split("\n", 1)
                    if not line:
                        continue
                    self._process_command(client_socket, line.strip(), client_address)

        except (ConnectionError, OSError) as exc:
            self.logger.error("[Client %s] connection error: %s", client_address, exc)
        finally:
            client_socket.close()
            self.logger.info("[Client %s] disconnected", client_address)

    def _process_command(
        self,
        client_socket: socket.socket,
        command: str,
        client_address: tuple[str, int] = ("unknown", 0),
    ) -> None:
        """Execute a single client command and return the server response."""
        command = command.strip()
        if not command:
            return

        if command == "LIST_FILES":
            file_names = self.file_service.list_files()
            self.logger.info(
                "[Client %s] LIST_FILES -> %d file(s)",
                client_address,
                len(file_names),
            )
            response = self.protocol.build_file_list_response(file_names)
            client_socket.sendall(response)
            return

        if command.startswith("DOWNLOAD|"):
            file_name = command.split("|", 1)[1].strip()
            if not file_name:
                self.logger.warning(
                    "[Client %s] DOWNLOAD missing filename", client_address
                )
                client_socket.sendall(self.protocol.build_error_response())
                return

            try:
                file_path = self.file_service.get_file_path(file_name)
            except FileNotFoundError:
                self.logger.warning(
                    "[Client %s] DOWNLOAD file not found: %s",
                    client_address,
                    file_name,
                )
                client_socket.sendall(self.protocol.build_error_response())
                return

            file_size = file_path.stat().st_size
            self.logger.info(
                "[Client %s] DOWNLOAD %s (%d bytes)",
                client_address,
                file_path.name,
                file_size,
            )
            client_socket.sendall(
                self.protocol.build_file_info_response(file_path.name, file_size)
            )

            with file_path.open("rb") as file_handle:
                while True:
                    chunk = file_handle.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
            return

        self.logger.warning(
            "[Client %s] Invalid command: %s", client_address, command
        )
        client_socket.sendall(self.protocol.build_error_response("Lệnh không hợp lệ"))


def main() -> None:
    """Run the TCP file-sharing server from command line."""
    server = TCPServer(
        host="0.0.0.0", port=5000, shared_dir=PROJECT_ROOT / "shared_files"
    )
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
