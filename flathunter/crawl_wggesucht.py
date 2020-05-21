# coding= UTF-8

import logging
import re

import requests
from bs4 import BeautifulSoup


class CrawlWgGesucht:
    __log__ = logging.getLogger(__name__)
    URL_PATTERN = re.compile(r'https://www\.wg-gesucht\.de')

    def __init__(self, config):
        logging.getLogger("requests").setLevel(logging.WARNING)
        self.config = config

    def get_results(self, search_url, ids_to_exclude):
        self.__log__.debug("Got search URL %s" % search_url)

        # load first page
        page_no = 0
        soup = self.get_page(search_url, page_no)
        no_of_pages = 0  # TODO get it from soup
        self.__log__.info('Found pages: ' + str(no_of_pages))

        # get data from first page
        entries = self.extract_data(soup, ids_to_exclude)
        self.__log__.debug('Number of found entries: ' + str(len(entries)))

        # iterate over all remaining pages
        while (page_no + 1) < no_of_pages:  # page_no starts with 0, no_of_pages with 1
            page_no += 1
            self.__log__.debug('Checking page %i' % page_no)
            soup = self.get_page(search_url, page_no)
            entries.extend(self.extract_data(soup, ids_to_exclude))
            self.__log__.debug('Number of found entries: ' + str(len(entries)))

        return entries

    def get_page(self, search_url, page_no):
        resp = requests.get(search_url)  # TODO add page_no in url
        if resp.status_code != 200:
            self.__log__.error("Got response (%i): %s" % (resp.status_code, resp.content))
        return BeautifulSoup(resp.content, 'lxml')

    def extract_data(self, soup, ids_to_exclude):
        entries = []

        findings = soup.find_all(lambda e: e.has_attr('id') and e['id'].startswith('liste-'))
        existingFindings = list(
            filter(lambda e: e.has_attr('class') and not 'display-none' in e['class'], findings))

        baseurl = 'https://www.wg-gesucht.de/'

        for index,row in enumerate(existingFindings):
            #print "Current Index is: "+ str(index) + "\n"
            #print row 
            infostring = row.find(
                lambda e: e.name == "div" and e.has_attr('class') and 'list-details-panel-inner' in e[
                    'class']).p.text.strip()
            #print(infostring)
            detail = row.find_all(lambda e: e.name == "a" and e.has_attr('class') and 'detailansicht' in e['class']);
            url = baseurl + detail[0]["href"]
            id = int(url.split('.')[-2])
            if id in ids_to_exclude:
                continue
            rooms = re.findall(r'\der WG', infostring)[0][:1]
            date = re.findall(r'\d{2}.\d{2}.\d{4}', infostring)[0]
            title = detail[2].text.strip()
            size_price = detail[0].text.strip()
            price = re.findall(r'\d{2,4}\s€', size_price)[0]
            size = re.findall(r'\d{2,4}\sm²', size_price)[0]

            details = {
                'id': id,
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

    def load_address(self, url):
        # extract address from expose itself
        r = requests.get(url)
        flat = BeautifulSoup(r.content, 'lxml')
        address = ' '.join(flat.find('div', {"class": "col-sm-4 mb10"}).find("a", {"href": "#"}).text.strip().split())
        return address