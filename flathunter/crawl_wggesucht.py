import logging
import re

import requests
from bs4 import BeautifulSoup


class CrawlWgGesucht:
    __log__ = logging.getLogger(__name__)
    URL_PATTERN = re.compile(r'https://www\.wg-gesucht\.de')

    def __init__(self):
        logging.getLogger("requests").setLevel(logging.WARNING)

    def get_results(self, search_url):
        self.__log__.debug("Got search URL %s" % search_url)

        # load first page
        page_no = 0
        soup = self.get_page(search_url, page_no)
        no_of_pages = 0  # TODO get it from soup
        self.__log__.info('Found pages: ' + str(no_of_pages))

        # get data from first page
        entries = self.extract_data(soup)
        self.__log__.debug('Number of found entries: ' + str(len(entries)))

        # iterate over all remaining pages
        while (page_no + 1) < no_of_pages:  # page_no starts with 0, no_of_pages with 1
            page_no += 1
            self.__log__.debug('Checking page %i' % page_no)
            soup = self.get_page(search_url, page_no)
            entries.extend(self.extract_data(soup))
            self.__log__.debug('Number of found entries: ' + str(len(entries)))

        return entries

    def get_page(self, search_url, page_no):
        resp = requests.get(search_url)  # TODO add page_no in url
        if resp.status_code != 200:
            self.__log__.error("Got response (%i): %s" % (resp.status_code, resp.content))
        return BeautifulSoup(resp.content, 'lxml')

    def extract_data(self, soup):
        entries = list()

        findings = soup.find_all(lambda e: e.has_attr('id') and e['id'].startswith('liste-'))
        existing_findings = list(
            [e for e in findings if e.has_attr('class') and not 'display-none' in e['class']])

        base_url = 'https://www.wg-gesucht.de/'
        for row in existing_findings:
            title_row = row.find('h3', {"class": "truncate_title"})
            title = title_row.text.strip()
            url = base_url + title_row.find('a')['href']
            detail_string = row.find("div", { "class": "col-xs-11" }).text.strip().split("|")
            details_array = list(map(lambda s: re.sub(' +', ' ', re.sub('\W', ' ', s.strip())), detail_string))
            numbers_row = row.find("div", { "class": "middle" })
            price = numbers_row.find("div", { "class": "col-xs-3" }).text.strip()
            rooms = re.findall(r'\d Zimmer', details_array[0])[0][:1]
            date = re.findall(r'\d{2}.\d{2}.\d{4}', numbers_row.find("div", { "class": "text-center" }).text)[0]
            size = re.findall(r'\d{2,4}\sm²', numbers_row.find("div", { "class": "text-right" }).text)[0]

            details = {
                'id': int(url.split('.')[-2]),
                'url': url,
                'title': "%s ab dem %s" % (title, date),
                'price': price,
                'size': size,
                'rooms': rooms + " Zi.",
                'address': url
            }
            entries.append(details)

        self.__log__.debug('extracted: ' + str(entries))

        return entries

    @staticmethod
    def load_address(url):
        # extract address from expose itself
        r = requests.get(url)
        flat = BeautifulSoup(r.content, 'lxml')
        address = ' '.join(flat.find('div', {"class": "col-sm-4 mb10"}).find("a", {"href": "#"}).text.strip().split())
        return address
