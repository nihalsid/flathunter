import logging
import requests
import re
from bs4 import BeautifulSoup


class CrawlImmobilienscout:
    __log__ = logging.getLogger(__name__)
    URL_PATTERN = re.compile(r'https://www\.immobilienscout24\.de')
    RESULT_LIMIT = 50

    def __init__(self):
        logging.getLogger("requests").setLevel(logging.WARNING)

    def get_results(self, search_url):
        # convert to paged URL
        # if '/P-' in search_url:
        #     search_url = re.sub(r"/Suche/(.+?)/P-\d+", "/Suche/\1/P-{0}", search_url)
        # else:
        #     search_url = re.sub(r"/Suche/(.+?)/", r"/Suche/\1/P-{0}/", search_url)
        if '&pagenumber' in search_url:
            search_url = re.sub(r"&pagenumber=[0-9]", "&pagenumber={0}", search_url)
        else:
            search_url = search_url + '&pagenumber={0}'
        self.__log__.debug("Got search URL %s" % search_url)

        # load first page to get number of entries
        page_no = 1
        soup = self.get_page(search_url, page_no)
        try:
            no_of_results = int(
                soup.find_all(lambda e: e.has_attr('data-is24-qa') and e['data-is24-qa'] == 'resultlist-resultCount')[
                    0].text)
        except IndexError:
            self.__log__.debug('Index Error occurred')
        # get data from first page
        entries = self.extract_data(soup)

        # iterate over all remaining pages
        while len(entries) < min(no_of_results, self.RESULT_LIMIT):
            self.__log__.debug(
                'Next Page, Number of entries : ' + str(len(entries)) + "no of resulst: " + str(no_of_results))
            page_no += 1
            soup = self.get_page(search_url, page_no)
            cur_entry = self.extract_data(soup)
            if cur_entry is list():
                break
            entries.extend(cur_entry)
        return entries

    def get_page(self, search_url, page_no):
        resp = requests.get(search_url.format(page_no))
        if resp.status_code != 200:
            self.__log__.error("Got response (%i): %s" % (resp.status_code, resp.content))
        return BeautifulSoup(resp.content, 'html.parser')

    def extract_data(self, soup):
        entries = list()

        title_elements = soup.find_all(
            lambda e: e.name == 'a' and e.has_attr('class') and 'result-list-entry__brand-title-container' in e[
                'class'])
        expose_ids = list()
        expose_urls = list()
        for link in title_elements:
            expose_id = int(link.get('href').split('/')[-1].replace('.html', ''))
            expose_ids.append(expose_id)
            if len(str(expose_id)) > 5:
                expose_urls.append('https://www.immobilienscout24.de/expose/' + str(expose_id))
            else:
                expose_urls.append(link.get('href'))
        self.__log__.debug(expose_ids)

        attr_container_els = soup.find_all(lambda e: e.has_attr('data-is24-qa') and e['data-is24-qa'] == "attributes")
        address_fields = soup.find_all(lambda e: e.has_attr('class') and 'result-list-entry__address' in e['class'])
        for idx, title_el in enumerate(title_elements):
            attr_els = attr_container_els[idx].find_all('dd')
            try:
                address = address_fields[idx].text.strip()
            except:
                address = "No address given"
            if len(attr_els) > 2:
                details = {
                    'id': expose_ids[idx],
                    'url': expose_urls[idx],
                    'title': title_el.text.strip().replace('NEU', ''),
                    'price': attr_els[0].text.strip().split(' ')[0].strip(),
                    'size': attr_els[1].text.strip().split(' ')[0].strip() + " qm",
                    'rooms': attr_els[2].text.strip().split(' ')[0].strip() + " Zi.",
                    'address': address
                }
            # print entries
            exist = False
            for x in entries:
                if expose_id == x["id"]:
                    exist = True
                    break
                else:
                    continue
            if not exist:
                entries.append(details)

        self.__log__.debug('extracted: ' + str(entries))
        return entries
