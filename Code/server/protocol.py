"""Utilities for encoding and decoding the TCP message protocol.

The project uses a simple line-based protocol between the client and the
server. Each request is sent as a text command terminated by a newline,
while server responses are serialized to strings/binary payloads in a
consistent format.
"""

from __future__ import annotations

from typing import Iterable


class MessageProtocol:
    """Build network messages and extract commands from incoming data."""

    @staticmethod
    def parse_command(data: bytes) -> str:
        """Decode a raw socket payload into a plain-text command without stripping newline separators."""
        return data.decode("utf-8", errors="replace").replace("\r", "")

    @staticmethod
    def build_file_list_response(file_names: Iterable[str]) -> bytes:
        """Build the FILE_LIST response as: FILE_LIST||length\n[name1]\n[name2]..."""
        names = sorted(str(name) for name in file_names)
        header = f"FILE_LIST||{len(names)}\n"
        if names:
            header += "\n".join(names) + "\n"
        return header.encode("utf-8")

    @staticmethod
    def build_file_info_response(file_name: str, file_size: int) -> bytes:
        """Build the header used before sending binary file data."""
        return f"FILE_INFO|{file_name}|{file_size}\n".encode("utf-8")

    @staticmethod
    def build_error_response(message: str = "Tệp tin không tồn tại trên Server") -> bytes:
        """Build an error response in the format required by the project."""
        return f"ERROR|FILE_NOT_FOUND|0\n{message}\n".encode("utf-8")
