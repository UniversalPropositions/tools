import unittest
from up2 import parse


class TestParse(unittest.TestCase):

    def setUp(self):
        pass

    def test_run(self):
        parse.parse("en-test", "en")
        parse.parse("en-test", "pl")

    def test_attack(self):
        pass

    def tearDown(self):
        pass
