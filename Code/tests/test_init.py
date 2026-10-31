import importlib
import pathlib
import sys
import unittest


class TestProjectInitialization(unittest.TestCase):
    def test_root_entry_point_exists(self):
        project_root = pathlib.Path(__file__).resolve().parents[2]
        self.assertTrue(
            (project_root / "main.py").exists(),
            "Expected a root-level main.py entry point for the application.",
        )

    def test_code_main_module_is_importable(self):
        project_root = pathlib.Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(project_root))
        module = importlib.import_module("Code.main")
        self.assertTrue(hasattr(module, "main"), "Code.main should expose a main() function.")


if __name__ == "__main__":
    unittest.main()
