import requests

from lxml import etree
import xmltodict

import logging
from typing import Iterable

import requests
from lxml.html import HtmlElement

from dutch_news_scrapers.scraper import TextScraper, Scraper
from dutch_news_scrapers.tools import response_to_dom


class RTVNoordScraper(Scraper):
    DOMAIN = "https://www.denhaagcentraal.net"
    PUBLISHER = "Den Haag Centraal"
    TEXT_CSS = ".article.article p"
    SITEMAP_URL = "https://www.denhaagcentraal.net/sitemap_index.xml"
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}
    
    def get_links(self) -> Iterable[str]:
        #r = requests.get("https://www.denhaagcentraal.net/sitemap_index.xml")
        #raw = xmltodict.parse(r.text)
        #data = [r["loc"] for r in raw["sitemapindex"]["sitemap"]]
        data = ["https://www.denhaagcentraal.net/post-sitemap4.xml"]
        for d in data:
            r = requests.get(d)
            raw = xmltodict.parse(r.text)
            urls = [r["loc"] for r in raw["urlset"]["url"]]
            for url in urls:
                if url.startswith("https://www.denhaagcentraal.net/nieuws/"):
                    yield url

        
    def meta_from_dom(self, dom: HtmlElement) -> dict:
        meta = {m.get('property', m.get('name')): m.get('content') for m in dom.cssselect("meta")}
        print(meta)
        tags = [v for (k,v) in meta.items() if k]
        art = dict(
            title = meta['og:title'],
            date = meta['article:published_time'],
           # section = meta['article:section'],
        )
        if 'article:modified_time' in meta:
            art['modified_date'] = meta['article:modified_time']
        return art





