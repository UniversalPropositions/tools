import unittest
import sys

sys.path.insert(0, "./up2")

import tests.test_download
import tests.test_preprocess
import tests.test_parse
import tests.test_merge_parse
import tests.test_wordalignment
import tests.test_merge_align
import tests.test_postprocess
import tests.test_spade_to_up
import tests.test_merge_ud_up

loader = unittest.TestLoader()
suite = unittest.TestSuite()

#steps before SPADE
suite.addTests(loader.loadTestsFromModule(tests.test_download))
suite.addTests(loader.loadTestsFromModule(tests.test_preprocess))
suite.addTests(loader.loadTestsFromModule(tests.test_parse))
suite.addTests(loader.loadTestsFromModule(tests.test_merge_parse))
suite.addTests(loader.loadTestsFromModule(tests.test_wordalignment))
suite.addTests(loader.loadTestsFromModule(tests.test_merge_align))
suite.addTests(loader.loadTestsFromModule(tests.test_postprocess))

#steps after SPADE
suite.addTests(loader.loadTestsFromModule(tests.test_spade_to_up))
suite.addTests(loader.loadTestsFromModule(tests.test_merge_ud_up))

runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)