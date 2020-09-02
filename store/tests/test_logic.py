from unittest import TestCase

from store.logic import operations


class LogicTestCase(TestCase):
    def test_plus(self):
        result = operations(3, 8, '+')
        self.assertEqual(11, result)

    def test_minus(self):
        result = operations(3, 8, '-')
        self.assertEqual(-5, result)

    def test_multiply(self):
        result = operations(3, 8, '*')
        self.assertEqual(24, result)


