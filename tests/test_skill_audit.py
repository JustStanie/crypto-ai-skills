import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_skill_audit.py"


class AuditAutomationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "scripts").mkdir()
        (self.root / "scripts" / "sync_skill_audit.py").write_bytes(SOURCE_SCRIPT.read_bytes())
        (self.root / "docs" / "audit").mkdir(parents=True)
        self.skills = self.root / ".agents" / "skills"
        self.skills.mkdir(parents=True)
        self.s1 = self.skills / "sample-method" / "SKILL.md"
        self.s1.parent.mkdir()
        self.s1.write_text("---\nname: sample-method\ndescription: 'Use to test one method.'\n---\n# Sample method\n\n## Workflow\nDo it safely.\n", encoding="utf-8")
        sha = hashlib.sha256(self.s1.read_bytes()).hexdigest()
        (self.root / "docs" / "audit" / "category-map.json").write_text(json.dumps({"categories": {"sample-method":"Testing"}}), encoding="utf-8")
        (self.root / "docs" / "audit" / "review-baseline.json").write_text(json.dumps({"original_review_date":"2026-10-31", "reviews":{"sample-method":{"reviewed_sha256":sha,"summary":"Historical static inspection only."}}}), encoding="utf-8")
        (self.root / "README.md").write_text("# Test repository\n\nSome original content.\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def execute(self, mode, expected):
        p = subprocess.run([sys.executable,str(self.root / "scripts" / "sync_skill_audit.py"),mode], capture_output=True, text=True)
        self.assertEqual(p.returncode,expected,msg=p.stdout+"\n"+p.stderr)

    def read_reg(self):
        return json.loads((self.root / "audit-register.json").read_text(encoding="utf-8"))

    def test_deterministic_generation_and_check(self):
        self.execute("--write",0)
        before = (self.root / "TECHNICAL_AUDIT.md").read_bytes()
        self.execute("--check",0)
        self.execute("--write",0)
        self.assertEqual(before, (self.root / "TECHNICAL_AUDIT.md").read_bytes())
        self.assertEqual(self.read_reg()[0]["review_status"],"historical_static_review_current")

    def test_changed_skill_invalidates_historical_review_without_faking_new_review(self):
        self.execute("--write",0)
        self.s1.write_text(self.s1.read_text(encoding="utf-8")+"\nAdditional new advice.\n",encoding="utf-8")
        self.execute("--check",1)
        self.execute("--write",0)
        self.assertEqual(self.read_reg()[0]["review_status"],"review_required_content_changed")
        self.assertEqual(json.loads((self.root / "AUDIT_VALIDATION_RESULTS.json").read_text())["static_validation"],"passed")
        self.execute("--check",0)

    def test_add_skill_and_remove_skill_both_update_inventory(self):
        self.execute("--write",0)
        p = self.skills / "new-specialist" / "SKILL.md"
        p.parent.mkdir()
        p.write_text("---\nname: new-specialist\ndescription: Newly introduced specialist.\n---\n# New Specialist\n",encoding="utf-8")
        self.execute("--check",1)
        self.execute("--write",0)
        self.assertEqual({r["skill"] for r in self.read_reg()}, {"sample-method","new-specialist"})
        other = next(r for r in self.read_reg() if r["skill"]=="new-specialist")
        self.assertEqual(other["review_status"],"review_required_new_or_unreviewed")
        self.assertEqual(other["category"],"Uncategorized")
        p.unlink()
        self.execute("--write",0)
        self.assertEqual(len(self.read_reg()),1)

    def test_invalid_frontmatter_fails_structural_validation(self):
        self.s1.write_text("# no metadata\n",encoding="utf-8")
        self.execute("--write",1)
        self.assertEqual(json.loads((self.root / "AUDIT_VALIDATION_RESULTS.json").read_text())["static_validation"],"failed")


if __name__ == "__main__":
    unittest.main()
