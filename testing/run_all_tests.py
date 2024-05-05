from testing.learning import TestFlashCard, TestDeck, TestJSON, TestHistorian, TestTargetTimeTracker, TestScheduler, \
    TestPicker, TestDeckManager
import unittest


def suite():
    """
        Gather all the testing from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    tests = [TestFlashCard, TestDeck, TestHistorian, TestTargetTimeTracker, TestScheduler, TestPicker, TestDeckManager]
    for test in tests:
        test_suite.addTest(unittest.makeSuite(test))
    return test_suite


if __name__ == '__main__':
    mySuit = suite()

    runner = unittest.TextTestRunner()
    runner.run(mySuit)
