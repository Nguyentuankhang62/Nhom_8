"""Entry point for running the UDM_11 server from the Code package."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Code.server.tcp_server import TCPServer


def main() -> None:
    """Start the TCP file-sharing server."""
    server = TCPServer(host="0.0.0.0", port=5000, shared_dir=PROJECT_ROOT / "shared_files")
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
