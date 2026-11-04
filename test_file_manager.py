import os, tempfile, threading, unittest
from Code.storage import FileManager


class TestFileManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fm = FileManager(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def read(self, p):
        with open(p, "rb") as f:
            return f.read()

    def test_stream_write(self):
        p = self.fm.save_stream("a.txt", [b"hello ", b"world"])
        self.assertEqual(self.read(p), b"hello world")
        self.assertFalse(os.path.exists(p + ".part"))

    def test_rename_on_conflict(self):
        self.fm.save_stream("a.txt", [b"1"])
        p2 = self.fm.save_stream("a.txt", [b"2"])
        p3 = self.fm.save_stream("a.txt", [b"3"])
        self.assertEqual(os.path.basename(p2), "a (1).txt")
        self.assertEqual(os.path.basename(p3), "a (2).txt")

    def test_overwrite(self):
        self.fm.save_stream("a.txt", [b"old"])
        p = self.fm.save_stream("a.txt", [b"new"], overwrite=True)
        self.assertEqual(os.path.basename(p), "a.txt")
        self.assertEqual(self.read(p), b"new")

    def test_error_removes_part_file(self):
        def bad():
            yield b"abc"
            raise ConnectionError("mất mạng")
        with self.assertRaises(ConnectionError):
            self.fm.save_stream("c.bin", bad())
        self.assertEqual(os.listdir(self.tmp.name), [])

    def test_path_traversal(self):
        p = self.fm.save_stream("../../evil.txt", [b"x"])
        self.assertEqual(os.path.dirname(p), self.fm.dir)

    def test_concurrent_same_name(self):
        paths = []
        ts = [threading.Thread(target=lambda: paths.append(
              self.fm.save_stream("d.txt", [b"x"] * 1000))) for _ in range(8)]
        [t.start() for t in ts]; [t.join() for t in ts]
        self.assertEqual(len(set(paths)), 8)


if __name__ == "__main__":
    unittest.main()
