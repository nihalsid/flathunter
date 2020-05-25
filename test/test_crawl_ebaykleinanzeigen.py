import unittest
from flathunter.crawl_ebaykleinanzeigen import CrawlEbayKleinanzeigen

class EbayKleinanzeigenCrawlerTest(unittest.TestCase):

    TEST_URL = 'https://www.ebay-kleinanzeigen.de/s-wohnung-mieten/berlin/preis:1000:1500/c203l3331+wohnung_mieten.qm_d:70,+wohnung_mieten.zimmer_d:2'

    def setUp(self):
        self.crawler = CrawlEbayKleinanzeigen()

    def test(self):
        soup = self.crawler.get_page(self.TEST_URL)
        self.assertIsNotNone(soup, "Should get a soup from the URL")
        entries = self.crawler.extract_data(soup)
        self.assertIsNotNone(entries, "Should parse entries from search URL")
        self.assertTrue(len(entries) > 0, "Should have at least one entry")
        self.assertTrue(entries[0]['id'] > 0, "Id should be parsed")
        self.assertTrue(entries[0]['url'].startswith("https://www.ebay-kleinanzeigen.de/s-anzeige"), u"URL should be an anzeige link")
        for attr in [ 'title', 'price', 'size', 'rooms', 'address' ]:
            self.assertIsNotNone(entries[0][attr], attr + " should be set")

