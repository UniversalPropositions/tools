import unittest
from up2 import spade_to_up

class TestSpadeToUP(unittest.TestCase):

    def setUp(self):
        pass

    def test_run(self):
        source = "UD_Hindi-HDTB/hi_hdtb-ud-dev.conllu"
        input_ud = "./tests/data/ud/hi/"
        input_spade = "./tests/data/spade/hi/"
        output = "./tests/data/up/hi/"
        spade_to_up.spade_to_up(source, input_ud, input_spade, output)

    def test_attack(self):
        pass

    def tearDown(self):
        pass
