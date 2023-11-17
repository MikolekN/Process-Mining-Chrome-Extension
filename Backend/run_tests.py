import unittest


class CustomTextTestResult(unittest.TextTestResult):
    COLOR_GREEN = '\033[92m'
    COLOR_RED = '\033[91m'
    COLOR_RESET = '\033[0m'

    def custom_write(self, status, test, err=None):
        color = self.COLOR_GREEN if status == "PASSED" else self.COLOR_RED
        self.stream.write(f"{color}{status}{self.COLOR_RESET}: {test.id()}")
        if err:
            self.stream.write(f" ({err[0].__name__}: {err[1]})")
        self.stream.write("\n")

    def addSuccess(self, test):
        super().addSuccess(test)
        self.custom_write("PASSED", test)

    def addError(self, test, err):
        super().addError(test, err)
        self.custom_write("FAILED", test, err)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.custom_write("FAILED", test, err)


if __name__ == '__main__':
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir='..', pattern='test_*.py')

    # Run the tests
    test_runner = unittest.TextTestRunner(resultclass=CustomTextTestResult)
    result = test_runner.run(test_suite)

    # Exit with an appropriate status code
    if not result.wasSuccessful():
        exit(1)
