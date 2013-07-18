from trellorss import TrelloRSS
from testvar import *
import unittest

class TestingRSS(unittest.TestCase):
	"""
	To run these tests, create a file called "testvar.py". In that file,
	define these variables:

	key={your api key}
	token={token to view your private boards}
	private_board={an id to a private board}
	public_board={an id to a public board}

	"""
	def test_get_all_private_all_fields(self):
		# Test 1 - get_all, retrieving all fields
		test_1 = TrelloRSS(key,token)
		test_1.get_all()

	def test_get_all_private_some_fields(self):
		# Test 2 - get_all, retrieving some fields
		test_2 = TrelloRSS(key,token)
		test_2.get_all(items=['boards'])

	def test_get_from_public_all(self):
		# Test 3 - get_from, with a public board and all fields
		test_3 = TrelloRSS(key)
		test_3.get_from(public_board, public_board=True, num=20)

	def test_get_from_public_some(self):
		# Test 4 - get_from, with a public board and some fields
		test_4 = TrelloRSS(key)
		test_4.get_from(public_board, public_board=True, items=['boards','lists'])

	def test_get_from_private_all(self):
		#  Test 5 - get_from, with a private board and all fields
		test_5 = TrelloRSS(key,token)
		test_5.get_from(private_board, public_board=False)

	def test_get_from_private_some(self):
		# Test 6 - get_from, with a private board and some fields
		test_6 = TrelloRSS(key,token)
		test_6.get_from(private_board, public_board=False,items=['cards','comments'])


if __name__ == '__main__':
	unittest.main()
