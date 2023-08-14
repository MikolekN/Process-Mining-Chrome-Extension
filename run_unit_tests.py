import unittest

if __name__ == '__main__':
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir='.', pattern='test_*.py')

    # Run the tests
    test_runner = unittest.TextTestRunner()
    result = test_runner.run(test_suite)

    # Exit with an appropriate status code
    if not result.wasSuccessful():
        exit(1)