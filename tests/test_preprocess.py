import unittest
from up2 import preprocess

class TestPreprocess(unittest.TestCase):

    def setUp(self):
        pass

    def test_run(self):
        preprocess.preprocess("en-test")

    def test_attack(self):
        pass

    def tearDown(self):
        pass
