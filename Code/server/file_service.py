"""Helpers for listing and reading files from the server shared directory."""

from __future__ import annotations

from pathlib import Path


class FileService:
    """Encapsulates access to the directory used to share files to clients."""

    def __init__(self, shared_dir: str | Path):
        self.shared_dir = Path(shared_dir).expanduser().resolve()
        self.shared_dir.mkdir(parents=True, exist_ok=True)

    def list_files(self) -> list[str]:
        """Return the names of all available files in the shared directory."""
        if not self.shared_dir.exists():
            self.shared_dir.mkdir(parents=True, exist_ok=True)

        files = [path for path in self.shared_dir.iterdir() if path.is_file()]
        return sorted(path.name for path in files)

    def get_file_path(self, file_name: str) -> Path:
        """Validate a requested filename and return the file path on disk."""
        safe_name = Path(file_name).name
        candidate = self.shared_dir / safe_name

        if not candidate.exists() or not candidate.is_file():
            raise FileNotFoundError(f"File not found: {safe_name}")

        return candidate
