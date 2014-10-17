import unittest

test_loader = unittest.TestLoader()
tests = test_loader.discover('tests')
test_runner = unittest.runner.TextTestRunner()
test_runner.run(tests)
