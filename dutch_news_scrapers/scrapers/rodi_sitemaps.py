import requests

from lxml import etree
import xmltodict

import logging
from typing import Iterable
import urllib

import requests
from lxml.html import HtmlElement

from dutch_news_scrapers.scraper import TextScraper, Scraper
from dutch_news_scrapers.tools import response_to_dom
import os
import xml.etree.ElementTree as et

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

class RodiScraper(Scraper):
    DOMAIN =  "https://www.rodi.nl/denhaag/"
    PUBLISHER = "Rodi Den Haag Sitemap"
    TEXT_CSS = "    component__article h1,h2,p"
    SITEMAP_URL = "https://www.rodi.nl/denhaag/sitemap"
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}
    
    def get_links(self) -> Iterable[str]:
        #r = requests.get("https://www.denhaagcentraal.net/sitemap_index.xml")
        #raw = xmltodict.parse(r.text)
        #data = [r["loc"] for r in raw["sitemapindex"]["sitemap"]]
        data = ["https://www.rodi.nl/denhaag/sitemap"]
        for d in data:
            r = requests.get(d, headers=headers)
            r.raise_for_status()
            raw = xmltodict.parse(r.content)
            urls = [r["loc"] for r in raw["urlset"]["url"]]
            for url in urls:
                if url.startswith("https://www.rodi.nl/denhaag/nieuws/"):
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





