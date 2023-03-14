import itertools
import logging
from typing import Iterable

import requests
from lxml.html import HtmlElement

from dutch_news_scrapers.scraper import TextScraper, Scraper
from dutch_news_scrapers.tools import response_to_dom


class RTVOostScraper(Scraper):
    DOMAIN = "rtvoost.nl"
    PUBLISHER = "RTV Oost"
    TEXT_CSS = ".article-content div.text, .article-content h2"
    API_URL = 'https://api.regiogroei.cloud/page/allenieuws?page=nieuws&id=allenieuws'
    HEADERS = {'Accept': 'application/vnd.groei.overijssel+json;v=5.0',
               'X-Groei-Platform': 'web'}
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}
    START_ARTICLE_ID = 2068942
    STOP_ARTICLE_ID = 2134925
    CONTINUE_ON_ERROR = True

    def get_links(self) -> Iterable[str]:
        # RTV Oost does not have an archive and API only goes 1 week back, so try all possible article numbers
        for id in range(self.START_ARTICLE_ID, self.STOP_ARTICLE_ID):
            while True:
                url = f"https://www.rtvoost.nl/nieuws/{id}/-"
                r = requests.head(url)
                logging.info(f"HTTP {r.status_code}: {url}")
                if r.status_code == 404:
                    break
                if r.status_code == 302:
                    url = r.headers['Location']
                    yield f"https://www.rtvoost.nl{url}"
                    break
                logging.warning("Unexpected status code! Sleeping 5 minutes and retrying")

    def meta_from_dom(self, dom: HtmlElement) -> dict:
        meta = {m.get('data-hid'): m.get('content') for m in dom.cssselect("meta")}
        tags = [v for (k,v) in meta.items() if k and k.startswith("article:tag-")]
        art = dict(
            title = meta['og:title'],
            date = meta['article:published_time'],
            section = meta['article:section'],
            image_url = meta['og:image'],
            tags = tags
        )
        if 'article:modified_time' in meta:
            art['modified_date'] = meta['article:modified_time']
        print(art)
        return art




