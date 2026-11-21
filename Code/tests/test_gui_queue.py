import pathlib
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch


project_root = pathlib.Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from Code.gui.queue_manager import DownloadQueueManager, DownloadTask
from Code.gui.main_window import MainWindow


class FakeTree:
    def __init__(self, items=None):
        self.items = dict(items or {})
        self.selected = ()

    def exists(self, item_id):
        return item_id in self.items

    def item(self, item_id, option=None):
        data = self.items[item_id]
        if option == "values":
            return data
        return {"values": data}

    def selection(self):
        return self.selected

    def get_children(self):
        return tuple(self.items.keys())

    def delete(self, item_id):
        self.items.pop(item_id, None)


class FakeVariable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


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

    def test_worker_count_respects_concurrency_limit(self):
        manager = DownloadQueueManager(lambda *_args: None, max_concurrent=2)
        condition = threading.Condition()
        release_workers = threading.Event()
        all_finished = threading.Event()
        started = []
        active = 0
        peak_active = 0
        completed = 0

        def controlled_download(task):
            nonlocal active, peak_active, completed
            with condition:
                active += 1
                peak_active = max(peak_active, active)
                started.append(task.filename)
                condition.notify_all()
            release_workers.wait(timeout=5)
            with condition:
                active -= 1
                completed += 1
                if completed == 3:
                    all_finished.set()

        manager._download = controlled_download
        try:
            for filename in ("one.bin", "two.bin", "three.bin"):
                manager.add_task(
                    DownloadTask(
                        filename=filename,
                        destination=pathlib.Path(filename),
                        host="127.0.0.1",
                        port=5000,
                    )
                )

            with condition:
                self.assertTrue(
                    condition.wait_for(lambda: len(started) == 2, timeout=3)
                )
                self.assertEqual(len(started), 2)
                self.assertEqual(peak_active, 2)

            release_workers.set()
            self.assertTrue(all_finished.wait(timeout=3))
            self.assertEqual(peak_active, 2)
        finally:
            release_workers.set()
            manager.shutdown()


class TestDestinationPolicies(unittest.TestCase):
    def make_window(self, policy):
        window = MainWindow.__new__(MainWindow)
        window.download_tree = FakeTree()
        window.conflict_var = FakeVariable(policy)
        window._destination_names = set()
        return window

    def test_skip_policy_does_not_reserve_existing_destination(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = pathlib.Path(temporary_directory) / "report.txt"
            target.write_text("existing", encoding="utf-8")
            window = self.make_window("Bỏ qua (Skip)")

            self.assertIsNone(
                window._resolve_destination("report.txt", target.parent)
            )

    def test_overwrite_policy_uses_existing_destination(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = pathlib.Path(temporary_directory) / "report.txt"
            target.write_text("existing", encoding="utf-8")
            window = self.make_window("Ghi đè (Overwrite)")

            self.assertEqual(
                window._resolve_destination("report.txt", target.parent),
                target,
            )

    def test_ask_policy_obeys_confirmation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = pathlib.Path(temporary_directory) / "report.txt"
            target.write_text("existing", encoding="utf-8")
            window = self.make_window("Hỏi xác nhận (Ask)")

            with patch(
                "Code.gui.main_window.messagebox.askyesno",
                return_value=True,
            ):
                self.assertEqual(
                    window._resolve_destination("report.txt", target.parent),
                    target,
                )

            with patch(
                "Code.gui.main_window.messagebox.askyesno",
                return_value=False,
            ):
                self.assertIsNone(
                    window._resolve_destination("report.txt", target.parent)
                )

    def test_auto_rename_uses_next_available_name(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = pathlib.Path(temporary_directory) / "report.txt"
            first_rename = target.with_name("report (1).txt")
            second_rename = target.with_name("report (2).txt")
            target.write_text("existing", encoding="utf-8")
            first_rename.write_text("existing", encoding="utf-8")
            window = self.make_window("Tự động đổi tên (Auto-rename)")
            window._destination_names.add(
                window._destination_key(second_rename)
            )

            self.assertEqual(
                window._resolve_destination("report.txt", target.parent),
                target.with_name("report (3).txt"),
            )


class TestDownloadListActions(unittest.TestCase):
    def make_window(self, items):
        window = MainWindow.__new__(MainWindow)
        window.download_tree = FakeTree(items)
        window.conflict_var = FakeVariable("Ghi đè (Overwrite)")
        window._destination_names = set()
        window._task_destinations = {}
        return window

    def test_active_task_cannot_be_removed_or_replaced(self):
        window = self.make_window(
            {
                "active.bin": ("active.bin", "1 KB", "10.0%", "5 KB/s", "1 giây", "Đang xử lý"),
                "done.bin": ("done.bin", "1 KB", "100.0%", "5 KB/s", "0 giây", "Thành công"),
            }
        )
        window.download_tree.selected = ("active.bin",)

        with patch("Code.gui.main_window.messagebox.showwarning") as warn_mock:
            window._remove_selected_downloads()
            warn_mock.assert_called_once()

        self.assertTrue(window.download_tree.exists("active.bin"))
        with tempfile.TemporaryDirectory() as temporary_directory:
            folder = pathlib.Path(temporary_directory)
            self.assertIsNone(window._resolve_destination("active.bin", folder))
            self.assertEqual(
                window._resolve_destination("done.bin", folder),
                folder / "done.bin",
            )

    def test_clear_finished_keeps_active_items_and_releases_keys(self):
        window = self.make_window(
            {
                "waiting.bin": ("waiting.bin", "1 KB", "0%", "—", "—", "Đang chờ"),
                "done.bin": ("done.bin", "1 KB", "100.0%", "5 KB/s", "0 giây", "Thành công"),
                "err.bin": ("err.bin", "1 KB", "0.0%", "—", "—", "Thất bại: Lỗi"),
            }
        )
        window._destination_names = {"k_wait", "k_done", "k_err"}
        window._task_destinations = {
            "waiting.bin": "k_wait",
            "done.bin": "k_done",
            "err.bin": "k_err",
        }

        window._clear_finished_downloads()

        self.assertEqual(window.download_tree.get_children(), ("waiting.bin",))
        self.assertEqual(window._destination_names, {"k_wait"})

    def test_retry_failed_enqueues_only_failed_items(self):
        window = self.make_window(
            {
                "done.bin": ("done.bin", "1 KB", "100.0%", "5 KB/s", "0 giây", "Thành công"),
                "err.bin": ("err.bin", "1 KB", "0.0%", "—", "—", "Thất bại: Lỗi"),
            }
        )
        enqueued = []
        window.enqueue_server_files = lambda names: enqueued.extend(names)

        window._retry_failed_downloads()

        self.assertEqual(enqueued, ["err.bin"])


if __name__ == "__main__":
    unittest.main()
