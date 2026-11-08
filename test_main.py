import unittest
from main import ExpertSystem, Graph, Tracer, bfs, dfs, ucs, greedy, astar, ids, dls, hill_climbing, executer


class TestExpert(unittest.TestCase):
    def setUp(self):
        self.es = ExpertSystem()

    def test_avant_succes(self):
        self.assertTrue(self.es.chainage_avant("guerison"))

    def test_arriere_succes(self):
        self.assertTrue(self.es.chainage_arriere("guerison"))

    def test_but_deja_present(self):
        self.assertTrue(self.es.chainage_avant("fievre"))

    def test_echec(self):
        self.assertFalse(self.es.chainage_avant("angine"))
        self.assertFalse(self.es.chainage_arriere("angine"))

    def test_cycle(self):
        self.es.rules.append({"if": ["guerison"], "then": "grippe_possible"})
        self.es.rules.append({"if": ["grippe_possible"], "then": "guerison"})
        self.es.facts = {"x"}
        self.assertFalse(self.es.chainage_arriere("guerison"))


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.g = Graph.exemple()

    def test_optimaux(self):
        for fn in (ucs, astar):
            r = executer(self.g, fn, verbose=False)
            self.assertEqual(r["cost"], 11)
            self.assertEqual(r["path"], ["S", "A", "B", "C", "D", "G"])

    def test_chemin_existe(self):
        for fn in (bfs, dfs, greedy, ids, hill_climbing):
            r = executer(self.g, fn, verbose=False)
            if fn is not hill_climbing:
                self.assertIsNotNone(r["path"], fn.__name__)
                self.assertEqual(r["path"][0], "S")
                self.assertEqual(r["path"][-1], "G")

    def test_bfs_moins_arcs(self):
        self.assertEqual(len(executer(self.g, bfs, verbose=False)["path"]), 4)

    def test_dls_limite(self):
        tr = Tracer(False)
        self.assertIsNone(dls(self.g, "S", "G", tr, limit=2))
        self.assertIsNotNone(dls(self.g, "S", "G", Tracer(False), limit=5))

    def test_aucun_chemin(self):
        self.g.add_vertex("Z")
        self.g.goal = "Z"
        for fn in (bfs, dfs, ucs, greedy, astar, ids):
            self.assertIsNone(executer(self.g, fn, verbose=False)["path"], fn.__name__)

    def test_depart_egal_objectif(self):
        self.g.goal = "S"
        self.assertEqual(executer(self.g, bfs, verbose=False)["path"], ["S"])


if __name__ == "__main__":
    unittest.main()