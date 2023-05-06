import re
import datetime
import locale
from typing import Iterable
import logging

import requests

from dutch_news_scrapers.scraper import TextScraper, Scraper, ArticleDoesNotExist
from dutch_news_scrapers.tools import response_to_dom, serialize

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}

class SallandTVScraper(Scraper):
    PAGES_URL = "https://www.sallandtv.nl/category/deventer/page/{page}/"
    PAGES_RANGE = 20
    PAGE_START = 2
    DOMAIN = "sallandtv.nl"
    PUBLISHER = "SallandTV"
    TEXT_CSS = "div.entry p"
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}


    def meta_from_dom(self, dom):
        article = {}
        headline = dom.cssselect("h2.post-title")
        if headline:
            article['title'] = headline[0].text_content()
        else:
            article['title'] = "no headline"
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = dom.cssselect("span.tie-date")
        date = date[0].text_content().strip()
        article['date'] = datetime.datetime.strptime(date, "%d %B %Y") 
    
    def get_links_from_page(self, page: int) -> Iterable[str]:
        if self.PAGES_URL is None:
            raise Exception("Please specify PAGES_URL")
        page = requests.get(self.PAGES_URL.format(page=page), headers=HEADERS)
        dom = response_to_dom(page)
        return self.get_links_from_dom(dom)


    def get_links_from_dom(self, dom):
        links = list(dom.cssselect('h2.post-title a'))
        for link in links:
            url = link.get("href")
            if 'tv-gids' in url:
                continue
            print(url)
            yield url

    def text_from_dom(self, dom):
        body_ps = dom.cssselect('div.entry p')
        text = "\n\n".join(p.text_content() for p in body_ps).strip()
        return text

    