import unittest
from pathlib import Path

from dlp_fusion import DLPFusion


ROOT_DIR = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT_DIR / "examples"


class TestSimpleKB(unittest.TestCase):
    def setUp(self):
        # use in-memory SQLite for tests
        self.dlp = DLPFusion(db_path=":memory:")
        self.dlp.connect()
        self.dlp.initialize_db()
        kb_path = EXAMPLES_DIR / "simple_kb.json"
        self.dlp.load_knowledge_base(str(kb_path))

    def tearDown(self):
        self.dlp.disconnect()

    def test_direct_type(self):
        # ABox 里直接声明 Tom:Human, Fluffy:Cat
        self.assertTrue(self.dlp.query("type", "Tom", "Human"))
        self.assertTrue(self.dlp.query("type", "Fluffy", "Cat"))

    def test_class_hierarchy_typing(self):
        # Human ⊑ Animal ⊑ LivingThing ⊑ Thing
        self.assertTrue(self.dlp.query("type", "Tom", "Animal"))
        self.assertTrue(self.dlp.query("type", "Tom", "LivingThing"))
        self.assertTrue(self.dlp.query("type", "Tom", "Thing"))

    def test_domain_and_range_typing(self):
        # hasParent(Tom, Mary) 且 hasParent 的 domain / range 都是 Animal
        self.assertTrue(self.dlp.query("type", "Tom", "Animal"))
        self.assertTrue(self.dlp.query("type", "Mary", "Animal"))

    def test_inverse_of(self):
        # hasParent(Tom, Mary) ⇒ hasChild(Mary, Tom) 已经在 Rel 里
        cur = self.dlp.conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*) FROM Rel
            WHERE property = ? AND from_ind = ? AND to_ind = ?
            """,
            ("hasChild", "Mary", "Tom"),
        )
        self.assertEqual(cur.fetchone()[0], 1)

    def test_subclass_query(self):
        # TBox: Cat ⊑ Animal ⊑ LivingThing ⊑ Thing
        self.assertTrue(self.dlp.query("sub", "Cat", "Animal"))
        self.assertTrue(self.dlp.query("sub", "Cat", "LivingThing"))
        self.assertTrue(self.dlp.query("sub", "Cat", "Thing"))

    def test_subproperty_query(self):
        # hasParent ⊑ hasAncestor
        self.assertTrue(self.dlp.query("subprop", "hasParent", "hasAncestor"))


if __name__ == "__main__":
    unittest.main()
