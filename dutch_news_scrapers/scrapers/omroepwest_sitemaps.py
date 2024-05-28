import requests

from lxml import etree
import xmltodict

import logging
from typing import Iterable

import requests
from lxml.html import HtmlElement

from dutch_news_scrapers.scraper import TextScraper, Scraper
from dutch_news_scrapers.tools import response_to_dom


class OmroepWestScraper(Scraper):
    DOMAIN = "omroepwest.nl"
    PUBLISHER = "Omroep West Sitemap"
    TEXT_CSS = ".article-content div.text, .article-content h2"
    API_URL = 'https://api.regiogroei.cloud/page/allenieuws?page=nieuws&id=allenieuws'
    HEADERS = {'Accept': 'application/vnd.groei.overijssel+json;v=5.0',
               'X-Groei-Platform': 'web'}
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}
   

    def get_links(self) -> Iterable[str]:
        r = requests.get("https://www.omroepwest.nl/sitemap/sitemap.xml.gz")
        raw = xmltodict.parse(r.text)
        data = [r["loc"] for r in raw["sitemapindex"]["sitemap"]]
        for d in data:
            r = requests.get(d)
            raw = xmltodict.parse(r.text)
            urls = [r["loc"] for r in raw["urlset"]["url"]]
            for url in urls:
                print(url)
                if 'vacatures' in url:
                    continue
                else:
                    if url.startswith("https://www.omroepwest.nl/nieuws/"):
                        yield url

    def meta_from_dom(self, dom: HtmlElement) -> dict:
        meta = {m.get('data-hid'): m.get('content') for m in dom.cssselect("meta")}
        tags = [v for (k,v) in meta.items() if k and k.startswith("article:tag-")]
        art = dict(
            title = meta['og:title'],
            date = meta['article:published_time'],
            section = meta['article:section'],
        #    image_url = meta['og:image'],
            tags = tags
        )
        if 'article:modified_time' in meta:
            art['modified_date'] = meta['article:modified_time']
        return art





