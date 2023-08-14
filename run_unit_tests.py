import unittest

COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'
COLOR_RESET = '\033[0m'


class CustomTextTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.write(f"{COLOR_GREEN}PASSED: {test.id()}{COLOR_RESET}\n")

    def addError(self, test, err):
        super().addError(test, err)
        self.stream.write(f"{COLOR_RED}ERROR: {test.id()} ({err[0].__name__}: {err[1]}){COLOR_RESET}\n")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stream.write(f"{COLOR_RED}FAILED: {test.id()} ({err[0].__name__}: {err[1]}){COLOR_RESET}\n")


if __name__ == '__main__':
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir='.', pattern='test_*.py')

    # Run the tests
    test_runner = unittest.TextTestRunner(resultclass=CustomTextTestResult)
    result = test_runner.run(test_suite)

    # Exit with an appropriate status code
    if not result.wasSuccessful():
        exit(1)
