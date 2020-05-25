import unittest
from flathunter.crawl_immowelt import CrawlImmowelt

class ImmoweltCrawlerTest(unittest.TestCase):

    TEST_URL = 'https://www.immowelt.de/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc'

    def setUp(self):
        self.crawler = CrawlImmowelt()

    def test(self):
        soup = self.crawler.get_page(self.TEST_URL)
        self.assertIsNotNone(soup, "Should get a soup from the URL")
        entries = self.crawler.extract_data(soup)
        self.assertIsNotNone(entries, "Should parse entries from search URL")
        self.assertTrue(len(entries) > 0, "Should have at least one entry")
        self.assertTrue(entries[0]['id'] > 0, "Id should be parsed")
        self.assertTrue(entries[0]['url'].startswith("https://www.immowelt.de/expose"), u"URL should be an exposé link")
        for attr in [ 'title', 'price', 'size', 'rooms', 'address' ]:
            self.assertIsNotNone(entries[0][attr], attr + " should be set")

