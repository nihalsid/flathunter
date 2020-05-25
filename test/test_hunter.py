import unittest
import yaml
from flathunter.crawl_immowelt import CrawlImmowelt
from flathunter.hunter import Hunter 
from flathunter.idmaintainer import IdMaintainer

class HunterTest(unittest.TestCase):

    DUMMY_CONFIG = """
urls:
  - https://www.immowelt.de/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc
    """

    def setUp(self):
        self.hunter = Hunter(yaml.safe_load(self.DUMMY_CONFIG))
        self.searchers = [CrawlImmowelt()]
        self.id_watch = IdMaintainer(":memory:")

    def test_hunt_flats(self):
        exposes = self.hunter.hunt_flats(self.searchers, self.id_watch)
        self.assertTrue(len(exposes) > 0, "Expected to find exposes")
