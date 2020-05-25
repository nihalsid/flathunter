import unittest
from flathunter.idmaintainer import IdMaintainer

class IdMaintainerTest(unittest.TestCase):

    TEST_URL = 'https://www.immowelt.de/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc'

    def setUp(self):
        self.maintainer = IdMaintainer(":memory:")

    def test_read_from_empty_db(self):
        self.assertEqual(0, len(self.maintainer.get()), "Expected empty db to return empty array")

    def test_read_after_write(self):
        self.maintainer.add(12345)
        self.assertEqual(12345, self.maintainer.get()[0], "Expected ID to be saved")
