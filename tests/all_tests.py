import coverage
import unittest

from user_tests import TestUsersAPI
from request_tests import TestRequestsAPI
from proposal_tests import TestProposalsAPI
from date_tests import TestDatesAPI


if __name__ == "__main__":
	COV = coverage.coverage(branch=True, include='main*')
	COV.start()

	users_test_suite = unittest.TestLoader().loadTestsFromTestCase(TestUsersAPI)
	requests_test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRequestsAPI)
	proposals_test_suite = unittest.TestLoader().loadTestsFromTestCase(TestProposalsAPI)
	dates_test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDatesAPI)

	all_tests = unittest.TestSuite([users_test_suite, requests_test_suite, proposals_test_suite, dates_test_suite])
	unittest.TextTestRunner(verbosity=2).run(all_tests)

	COV.stop()
	COV.report()