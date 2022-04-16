import unittest
from up2 import merge_ud_up

class TestMergeUDUP(unittest.TestCase):

    def setUp(self):
        pass

    def test_run(self):
        input_ud = "./tests/data/ud/hi/"
        input_up = "./tests/data/up/hi/"
        output = "./tests/data/ud-up/hi/"
        merge_ud_up.merge_ud_up(input_ud, input_up, output)

    def test_attack(self):
        pass

    def tearDown(self):
        pass
