import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "bin" / "prompt-lib"
SPEC = importlib.util.spec_from_file_location("prompt_lib_cli", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class PromptLibCliTests(unittest.TestCase):
    def test_parse_org_uses_only_prompt_subtree(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "example.org"
            path.write_text(
                "#+title: Example\n"
                "#+prompt_id: test.example\n\n"
                "* Prompt\n"
                "Hello {{NAME|world}}\n\n"
                "* Notes\n"
                "not prompt text\n",
                encoding="utf-8",
            )
            prompt = MODULE.parse_org(path)
            self.assertEqual(prompt.prompt_id, "test.example")
            self.assertEqual(prompt.title, "Example")
            self.assertEqual(prompt.body, "Hello {{NAME|world}}")

    def test_render_substitutes_values_and_defaults(self):
        rendered = MODULE.render(
            "Repo {{REPO}} mode {{MODE|REVIEW}} unresolved {{MISSING}}",
            {"REPO": "lost-rob0t/zara"},
        )
        self.assertEqual(
            rendered,
            "Repo lost-rob0t/zara mode REVIEW unresolved {{MISSING}}",
        )

    def test_parse_values_requires_assignment(self):
        with self.assertRaises(SystemExit):
            MODULE.parse_values(["BROKEN"])


if __name__ == "__main__":
    unittest.main()
