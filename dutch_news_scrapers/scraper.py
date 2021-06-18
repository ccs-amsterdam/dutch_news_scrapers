from typing import Optional

import requests
from lxml.html import Element
from lxml import html
import re

class Scraper:
    URL_MATCH = None
    DOMAIN = None

    def __init__(self, proxies: Optional[dict]=None):
        self.session = requests.session()
        if proxies:
            self.session.proxies.update(proxies)
        self.initialize()

    def initialize(self):
        pass

    def scrape_text(self, url: str):
        page = self.session.get(url)
        if "advertorial" in url:
            return
        page.raise_for_status()
        open("/tmp/test7.html", "w").write(page.text)
        tree = html.fromstring(page.text)
        return self.parse_html(tree)

    def parse_html(self, page: Element) -> str:
        raise NotImplementedError()

    def can_scrape(self, url: str) -> bool:
        """Can this scraper handle this url?"""
        pattern = self._get_url_match()
        return bool(re.match(pattern, url))

    def _get_url_match(self):
        if self.URL_MATCH:
            return self.URL_MATCH
        elif self.DOMAIN:
            return f"https?://([^/]*\\.)?{self.DOMAIN}/"
        else:
            raise Exception("Specify either DOMAIN or URL_MATCH")
