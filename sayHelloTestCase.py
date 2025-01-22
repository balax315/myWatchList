import unittest

from sayhello import say_hello


class SayHelloTestCase(unittest.TestCase):

    def setUp(self):
        print("setUp")
    def tearDown(self):
        print('tearDown')

    def test_sayhello(self):
        res = say_hello()
        self.assertEqual(res,"Hello!")

    def test_sayhello_to_someone(self):
        res = say_hello("tom")
        self.assertEqual(res,"Hello,tom!")


if __name__ == '__main__':
    unittest.main()