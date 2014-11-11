import unittest
import sys


if __name__ == "__main__":
    test_loader = unittest.TestLoader()
    tests = test_loader.discover('tests')
    test_runner = unittest.runner.TextTestRunner()
    result = test_runner.run(tests)
    status = len(result.errors) + len(result.failures)

    sys.exit(status)
