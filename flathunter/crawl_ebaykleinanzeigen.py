import logging
import requests
import re
from bs4 import BeautifulSoup


class CrawlEbayKleinanzeigen:
    __log__ = logging.getLogger(__name__)
    URL_PATTERN = re.compile(r'https://www\.ebay-kleinanzeigen\.de')

    def __init__(self):
        logging.getLogger("requests").setLevel(logging.WARNING)

    def get_results(self, search_url):
        self.__log__.debug("Got search URL %s" % search_url)

        soup = self.get_page(search_url)

        # get data from first page
        entries = self.extract_data(soup)
        self.__log__.debug('Number of found entries: ' + str(len(entries)))

        return entries

    def get_page(self, search_url):
        resp = requests.get(search_url)  # TODO add page_no in url
        if resp.status_code != 200:
            self.__log__.error("Got response (%i): %s" % (resp.status_code, resp.content))
        return BeautifulSoup(resp.content, 'html5lib')

    def extract_data(self, soup):
        entries = list()
        soup = soup.find(id="srchrslt-adtable")
        try:
            title_elements = soup.find_all(lambda e: e.has_attr('class') and 'ellipsis' in e['class'])
        except AttributeError:
            return entries
        expose_ids = soup.find_all("article", class_="aditem")

        # soup.find_all(lambda e: e.has_attr('data-adid'))
        # print(expose_ids)
        for idx, title_el in enumerate(title_elements):
            price = expose_ids[idx].find("strong").text
            tags = expose_ids[idx].find_all(class_="simpletag tag-small")
            url = "https://www.ebay-kleinanzeigen.de" + title_el.get("href")
            address = expose_ids[idx].find("div", {"class": "aditem-details"})
            address.find("strong").extract()
            address.find("br").extract()
            self.__log__.debug(address.text.strip())
            address = address.text.strip()
            address = address.replace('\n', ' ').replace('\r', '')
            address = " ".join(address.split())
            try:
                self.__log__.debug(tags[0].text)
                rooms = tags[0].text
            except IndexError:
                self.__log__.debug("Keine Zimmeranzahl gegeben")
                rooms = "Nicht gegeben"
            try:
                self.__log__.debug(tags[1].text)
                size = tags[1].text
            except IndexError:
                size = "Nicht gegeben"
                self.__log__.debug("Quadratmeter nicht angegeben")
            details = {
                'id': int(expose_ids[idx].get("data-adid")),
                'url': url,
                'title': title_el.text.strip(),
                'price': price,
                'size': size,
                'rooms': rooms,
                'address': address
            }
            entries.append(details)

        self.__log__.debug('extracted: ' + str(entries))

        return entries

    @staticmethod
    def load_address(url):
        # extract address from expose itself
        expose_html = requests.get(url).content
        expose_soup = BeautifulSoup(expose_html, 'html.parser')
        try:
            street_raw = expose_soup.find(id="street-address").text
        except AttributeError:
            street_raw = ""
        try:
            address_raw = expose_soup.find(id="viewad-locality").text
        except AttributeError:
            address_raw = ""
        address = address_raw.strip().replace("\n", "") + " " + street_raw.strip()

        return address
