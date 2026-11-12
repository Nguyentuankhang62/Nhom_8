import pathlib
import sys
import unittest


project_root = pathlib.Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from Code.gui.queue_manager import DownloadQueueManager, DownloadTask


class TestDownloadQueueManager(unittest.TestCase):
    def test_queue_rejects_tasks_after_shutdown(self):
        manager = DownloadQueueManager(lambda *_args: None, max_concurrent=1)
        manager.shutdown()

        with self.assertRaises(RuntimeError):
            manager.add_task(
                DownloadTask(
                    filename="file.txt",
                    destination=pathlib.Path("file.txt"),
                    host="127.0.0.1",
                    port=5000,
                )
            )

    def test_queue_rejects_invalid_worker_limits(self):
        for limit in (0, DownloadQueueManager.MAX_WORKERS + 1):
            with self.subTest(limit=limit):
                with self.assertRaises(ValueError):
                    DownloadQueueManager(
                        lambda *_args: None,
                        max_concurrent=limit,
                    )


if __name__ == "__main__":
    unittest.main()
