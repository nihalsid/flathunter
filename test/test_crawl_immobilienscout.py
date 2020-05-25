import unittest
from flathunter.crawl_immobilienscout import CrawlImmobilienscout

class ImmobilienscoutCrawlerTest(unittest.TestCase):

    TEST_URL = 'https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mieten?numberofrooms=2.0-&price=-1500.0&livingspace=70.0-&sorting=2&pagenumber=1'

    def setUp(self):
        self.crawler = CrawlImmobilienscout()

    def test(self):
        soup = self.crawler.get_page(self.TEST_URL, 1)
        self.assertIsNotNone(soup, "Should get a soup from the URL")
        entries = self.crawler.extract_data(soup)
        self.assertIsNotNone(entries, "Should parse entries from search URL")
        self.assertTrue(len(entries) > 0, "Should have at least one entry")
        self.assertTrue(entries[0]['id'] > 0, "Id should be parsed")
        self.assertTrue(entries[0]['url'].startswith("https://www.immobilienscout24.de/expose"), u"URL should be an exposé link")
        for attr in [ 'title', 'price', 'size', 'rooms', 'address' ]:
            self.assertIsNotNone(entries[0][attr], attr + " should be set")

