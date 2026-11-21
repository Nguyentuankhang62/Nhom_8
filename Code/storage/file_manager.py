"""Module Quản lý File Đĩa [Nguyễn Văn Việt - T06]
- Ghi stream xuống đĩa theo từng chunk, qua file tạm .part (lỗi/hủy -> xóa file tạm)
- Xử lý file trùng tên: đổi tên "a (1).txt" hoặc ghi đè (overwrite)
"""
import os
import re
import threading


class DiskWriteError(Exception):
    """Lỗi ghi đĩa (đĩa đầy, mất quyền, ...)."""


class FileManager:
    def __init__(self, download_dir, overwrite=False):
        self.dir = os.path.abspath(download_dir)
        self.overwrite = overwrite      # False: đổi tên khi trùng, True: ghi đè
        self._lock = threading.Lock()
        self._busy = set()              # các đường dẫn đang được luồng khác ghi
        os.makedirs(self.dir, exist_ok=True)

    @staticmethod
    def safe_name(name):
        """Bỏ đường dẫn và ký tự cấm (chống '../../')."""
        name = os.path.basename(name.replace("\\", "/"))
        return re.sub(r'[<>:"|?*]', "_", name).strip(" .") or "unnamed_file"

    def get_path(self, filename, overwrite=None):
        """Chọn đường dẫn lưu file, xử lý trùng tên."""
        overwrite = self.overwrite if overwrite is None else overwrite
        path = os.path.join(self.dir, self.safe_name(filename))
        base, ext = os.path.splitext(path)
        with self._lock:
            n = 0
            while path in self._busy or (os.path.exists(path) and not overwrite):
                n += 1
                path = f"{base} ({n}){ext}"
            self._busy.add(path)
        return path

    def save_stream(self, filename, chunks, overwrite=None, progress_cb=None):
        """Ghi iterable các chunk (bytes) xuống đĩa, trả về đường dẫn file."""
        path = self.get_path(filename, overwrite)
        tmp, written = path + ".part", 0
        try:
            with open(tmp, "wb") as f:
                for chunk in chunks:    # lỗi mạng từ chunks được ném nguyên vẹn
                    try:
                        f.write(chunk)
                    except OSError as e:
                        raise DiskWriteError(f"Lỗi ghi đĩa: {e}") from e
                    written += len(chunk)
                    if progress_cb:
                        progress_cb(written)
            os.replace(tmp, path)       # tải xong mới đổi tên chính thức
        except BaseException:           # lỗi đĩa, mất mạng, hủy tải...
            self._cleanup(tmp)
            raise
        finally:
            with self._lock:
                self._busy.discard(path)
        return path

    @staticmethod
    def _cleanup(tmp):
        if os.path.exists(tmp):
            os.remove(tmp)
