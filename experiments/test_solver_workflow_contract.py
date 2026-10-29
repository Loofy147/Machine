from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


class SolverWorkflowContractTests(unittest.TestCase):
    def workflow(self, name):
        return (WORKFLOWS / name).read_text(encoding="utf-8")

    def test_z3_version_is_pinned_and_reported(self):
        content = self.workflow("observation-recovery-z3.yml")
        self.assertIn("z3-solver==5.1.0.0", content)
        self.assertIn("version('z3-solver')", content)
        self.assertIn("--fail-on-unknown", content)

    def test_cvc5_version_is_pinned_and_reported(self):
        content = self.workflow("observation-recovery-cvc5.yml")
        self.assertIn("cvc5==1.4.1", content)
        self.assertIn("version('cvc5')", content)
        self.assertIn("--fail-on-unknown", content)

    def test_bitwuzla_version_remains_pinned_and_reported(self):
        content = self.workflow("observation-recovery-bitwuzla.yml")
        self.assertIn("bitwuzla==0.9.1", content)
        self.assertIn("version('bitwuzla')", content)

    def test_timeouts_are_not_redefined_as_proof_success(self):
        for name in (
            "observation-recovery-z3.yml",
            "observation-recovery-cvc5.yml",
        ):
            with self.subTest(workflow=name):
                content = self.workflow(name)
                self.assertIn("--timeout-ms 30000", content)
                self.assertIn("--fail-on-unknown", content)


if __name__ == "__main__":
    unittest.main()
