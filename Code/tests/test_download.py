"""Kiểm thử đa luồng, hàng đợi tải đồng thời, cô lập lỗi và SpeedTracker."""

import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from Code.gui.queue_manager import DownloadQueueManager, DownloadTask
from Code.queue_mgr.queue_manager import DownloadQueueManager as BasicQueueManager
from Code.utils.logger import close_logger
from Code.utils.speed_tracker import SpeedTracker


class TestDownloadAndConcurrency(unittest.TestCase):
    def test_speed_tracker_metrics(self):
        tracker = SpeedTracker(window_seconds=3.0)
        tracker.update(512)
        self.assertAlmostEqual(tracker.get_progress(1024), 50.0)
        tracker.update(512)
        self.assertAlmostEqual(tracker.get_progress(1024), 100.0)
        self.assertEqual(tracker.get_eta(1024), 0.0)

    def test_basic_queue_manager_respects_max_concurrent(self):
        qm = BasicQueueManager(max_concurrent=2)
        qm.add_task("file1.zip")
        qm.add_task("file2.zip")
        qm.add_task("file3.zip")

        t1 = qm.get_next_task()
        t2 = qm.get_next_task()
        self.assertEqual((t1, t2), ("file1.zip", "file2.zip"))
        self.assertIsNone(qm.get_next_task())

        qm.task_finished(t1)
        self.assertEqual(qm.get_next_task(), "file3.zip")

    def test_concurrent_downloads_and_fault_isolation(self):
        updates = []
        done_event = threading.Event()
        lock = threading.Lock()

        def on_update(filename, progress, speed, eta, status, size=None):
            with lock:
                updates.append((filename, progress, status))
                terminal = [
                    u
                    for u in updates
                    if u[2] == "Thành công" or u[2].startswith("Thất bại")
                ]
                if len({u[0] for u in terminal}) >= 3:
                    done_event.set()

        manager = DownloadQueueManager(on_update, max_concurrent=2)

        def fake_download(task: DownloadTask):
            time.sleep(0.05)
            if task.filename == "corrupt.bin":
                raise ConnectionResetError("Mất kết nối giữa chừng")
            task.destination.write_bytes(b"OK")
            manager.on_update(task.filename, 100.0, "100 KB/s", "0 giây", "Thành công")

        try:
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                with patch.object(manager, "_download", side_effect=fake_download):
                    for name in ("good1.txt", "corrupt.bin", "good2.txt"):
                        manager.add_task(
                            DownloadTask(
                                filename=name,
                                destination=tmp_path / name,
                                host="127.0.0.1",
                                port=5000,
                            )
                        )
                    finished = done_event.wait(timeout=3.0)

                self.assertTrue(finished, "Hàng đợi không hoàn thành kịp thời gian")
                self.assertTrue((tmp_path / "good1.txt").exists())
                self.assertTrue((tmp_path / "good2.txt").exists())
                self.assertFalse((tmp_path / "corrupt.bin").exists())

                final_status = {name: status for name, _p, status in updates}
                self.assertEqual(final_status["good1.txt"], "Thành công")
                self.assertEqual(final_status["good2.txt"], "Thành công")
                self.assertTrue(final_status["corrupt.bin"].startswith("Thất bại"))
        finally:
            manager.shutdown()
            close_logger(manager.error_handler.logger)


if __name__ == "__main__":
    unittest.main()
