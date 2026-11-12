import pathlib
import sys
import unittest
from unittest.mock import patch


project_root = pathlib.Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from Code.gui.main_window import MainWindow


class FakeListbox:
    def __init__(self, items, selected=()):
        self.items = list(items)
        self.selected = tuple(selected)

    def curselection(self):
        return self.selected

    def delete(self, index):
        self.items.pop(index)

    def get(self, index):
        return self.items[index]

    def size(self):
        return len(self.items)


class FakeProgress:
    def __init__(self):
        self.value = None

    def __setitem__(self, key, value):
        if key == "value":
            self.value = value


class FakeLabel:
    def __init__(self):
        self.text = None

    def config(self, **kwargs):
        self.text = kwargs.get("text")


class FakeRoot:
    def __init__(self):
        self.callbacks = []

    def after(self, delay, callback):
        self.callbacks.append((delay, callback))


class TestDownloadQueue(unittest.TestCase):
    def test_running_file_cannot_be_removed(self):
        window = MainWindow.__new__(MainWindow)
        window.queue_listbox = FakeListbox(
            ["active.bin", "waiting.bin"],
            selected=(0,),
        )
        window.is_downloading = True

        with patch("Code.gui.main_window.messagebox.showwarning") as warning:
            window.remove_from_queue()

        self.assertEqual(
            window.queue_listbox.items,
            ["active.bin", "waiting.bin"],
        )
        warning.assert_called_once()

    def test_finish_does_not_remove_next_file_if_active_file_is_missing(self):
        window = MainWindow.__new__(MainWindow)
        window.queue_listbox = FakeListbox(["waiting.bin"])
        window.current_file = "active.bin"
        window.is_downloading = True
        window.progress = FakeProgress()
        window.progress_label = FakeLabel()
        window.root = FakeRoot()

        window.finish_download()

        self.assertEqual(window.queue_listbox.items, ["waiting.bin"])
        self.assertEqual(window.progress_label.text, "Hoàn thành: active.bin")
        self.assertFalse(window.is_downloading)
        self.assertIsNone(window.current_file)
        self.assertEqual(
            window.root.callbacks,
            [(500, window.start_next_download)],
        )


if __name__ == "__main__":
    unittest.main()
