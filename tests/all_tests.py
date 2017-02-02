import coverage
import unittest

from user_tests import TestUsersAPI






if __name__ == "__main__":
	COV = coverage.coverage(branch=True, include='main*')
	COV.start()

	users_test_suite = unittest.TestLoader().loadTestsFromTestCase(TestUsersAPI)

	all_tests = unittest.TestSuite([users_test_suite])
	unittest.TextTestRunner(verbosity=2).run(all_tests)

	COV.stop()
	COV.report()