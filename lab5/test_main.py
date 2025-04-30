import unittest
from main import RegexParser, NFABuilder, Literal, Concatenation, Alternation, Star, Group

class TestRegexParser(unittest.TestCase):

    def test_single_literal(self):
        parser = RegexParser("a")
        ast = parser.parse()
        self.assertIsInstance(ast, Literal)
        self.assertEqual(ast.char, "a")

    def test_concatenation(self):
        parser = RegexParser("ab")
        ast = parser.parse()
        self.assertIsInstance(ast, Concatenation)
        self.assertIsInstance(ast.left, Literal)
        self.assertEqual(ast.left.char, "a")
        self.assertIsInstance(ast.right, Literal)
        self.assertEqual(ast.right.char, "b")

    def test_alternation(self):
        parser = RegexParser("a|b")
        ast = parser.parse()
        self.assertIsInstance(ast, Alternation)
        self.assertEqual(ast.left.char, "a")
        self.assertEqual(ast.right.char, "b")

    def test_star(self):
        parser = RegexParser("a*")
        ast = parser.parse()
        self.assertIsInstance(ast, Star)
        self.assertEqual(ast.node.char, "a")

    def test_group(self):
        parser = RegexParser("(a)")
        ast = parser.parse()
        self.assertIsInstance(ast, Group)
        self.assertIsInstance(ast.node, Literal)
        self.assertEqual(ast.node.char, "a")

    def test_complex_expression(self):
        parser = RegexParser("(a|b)*c")
        ast = parser.parse()
        self.assertIsInstance(ast, Concatenation)
        self.assertIsInstance(ast.left, Star)
        self.assertIsInstance(ast.right, Literal)

class TestNFABuilder(unittest.TestCase):

    def test_nfa_for_literal(self):
        builder = NFABuilder()
        nfa = builder.build(Literal("a"))
        self.assertEqual(len(nfa.start.transitions), 1)
        self.assertIn("a", nfa.start.transitions)
        self.assertIn(nfa.end, nfa.start.transitions["a"])

    def test_nfa_for_concatenation(self):
        builder = NFABuilder()
        left = Literal("a")
        right = Literal("b")
        nfa = builder.build(Concatenation(left, right))
        self.assertTrue(nfa.start.transitions)

    def test_nfa_for_alternation(self):
        builder = NFABuilder()
        nfa = builder.build(Alternation(Literal("a"), Literal("b")))
        self.assertIn(None, nfa.start.transitions)
        self.assertEqual(len(nfa.start.transitions[None]), 2)

    def test_nfa_for_star(self):
        builder = NFABuilder()
        nfa = builder.build(Star(Literal("a")))
        self.assertIn(None, nfa.start.transitions)

if __name__ == '__main__':
    unittest.main()
