import importlib
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestWorkflowArtifacts(unittest.TestCase):
    def test_workflow_files_exist(self):
        for rel in (
            "docs/superpowers/specs/2026-11-24-superpowers-workflow-design.md",
            "docs/superpowers/plans/2026-11-24-superpowers-workflow.md",
            "docs/superpowers/workflow-record.md",
        ):
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_readme_links_local_server_and_record(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("http://127.0.0.1:5000/", text)
        self.assertIn("docs/superpowers/workflow-record.md", text)

    def test_dc_bias_entry_point_reexports_calculators(self):
        module = importlib.import_module("dc_bias")
        for name in ("calculate_bias", "calculate_fixed", "calculate_emitter"):
            self.assertTrue(hasattr(module, name), name)
