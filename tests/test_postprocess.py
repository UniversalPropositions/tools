import unittest
from up2 import postprocess

class TestPostprocess(unittest.TestCase):

    def setUp(self):
        pass

    def test_run(self):
        postprocess.postprocess("en-test")

    def test_attack(self):
        pass

    def tearDown(self):
        pass
