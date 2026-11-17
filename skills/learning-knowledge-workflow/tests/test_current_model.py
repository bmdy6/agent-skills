import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
AGENT_SKILLS = ROOT.parents[2]

LEGACY_MARKERS = (
    "LEARNING_" + "VAULT",
    "10-" + "wiki/",
    "20-个人/10-" + "草稿箱/",
    "20-个人/20-" + "调研报告/",
    "00-总览/" + "知识管理手册.md",
    "00-总览/" + "寓言写作 Prompt.md",
)


class CurrentKnowledgeModelTest(unittest.TestCase):
    def test_routes_point_to_existing_references(self):
        routes = json.loads((ROOT / "routes.json").read_text(encoding="utf-8"))["routes"]
        self.assertGreaterEqual(len(routes), 5)
        for route in routes:
            target = ROOT / route["path"]
            self.assertTrue(target.is_file(), route)

    def test_active_skill_tree_has_no_legacy_knowledge_paths(self):
        hits = []
        this_file = Path(__file__).resolve()
        for path in AGENT_SKILLS.rglob("*"):
            if not path.is_file() or "disabled-skills" in path.parts:
                continue
            if path.resolve() == this_file:
                continue
            if path.suffix not in {".md", ".json", ".py", ".yaml", ".yml"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for marker in LEGACY_MARKERS:
                if marker in text:
                    hits.append(f"{path.relative_to(AGENT_SKILLS)}: {marker}")
        self.assertEqual(hits, [])

    def test_skill_declares_current_truth_and_publish_boundary(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("knowledge-mcp", skill)
        self.assertIn("personal/调研/", skill)
        self.assertIn("personal/学习-需要学习的.md", skill)
        self.assertIn("Workbench", skill)
        self.assertIn("阅读/沉淀", skill)

    def test_obsolete_local_scripts_are_gone(self):
        self.assertFalse((ROOT / "scripts" / "add_topic.py").exists())
        self.assertFalse((ROOT / "scripts" / "vault_audit.py").exists())


if __name__ == "__main__":
    unittest.main()
