import requests

from lxml import etree
import xmltodict

import logging
from typing import Iterable

import requests
from lxml.html import HtmlElement

from dutch_news_scrapers.scraper import TextScraper, Scraper
from dutch_news_scrapers.tools import response_to_dom


class BlckBxScraper(Scraper):
    DOMAIN = "blckbx.tv"
    PUBLISHER = "Blckbx"
    TEXT_CSS = ".article-content div.text, .article-content h2"
    HEADERS = {'Accept': 'application/vnd.groei.overijssel+json;v=5.0',
               'X-Groei-Platform': 'web'}
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}
    CONTINUE_ON_ERROR = True

    def get_links(self) -> Iterable[str]:
        r = requests.get("https://www.blckbx.tv/sitemaps-1-sitemap.xml")
        raw = xmltodict.parse(r.text)
        data = [r["loc"] for r in raw["sitemapindex"]["sitemap"]]
        for d in data:
            r = requests.get(d)
            raw = xmltodict.parse(r.text)
            import json; print(json.dumps(raw, indent=2, default=str))
            urls = [r["loc"] for r in raw["urlset"]["url"]]
            for url in urls:
                if url.startswith(("https://www.blckbx.tv/binnenland/", "https://www.blckbx.tv/buitenland/", "https://www.blckbx.tv/economie/", "https://www.blckbx.tv/corona/",
                                   "https://www.blckbx.tv/gezondheid", "https://www.blckbx.tv/klimaat", "https://www.blckbx.tv/tech-media")):
                    yield url

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





