import unittest
from up2 import download


class TestDownload(unittest.TestCase):

    def setUp(self):
        pass

    def test_run(self):
        download.download("en-test")

    def test_attack(self):
        pass

    def tearDown(self):
        pass
