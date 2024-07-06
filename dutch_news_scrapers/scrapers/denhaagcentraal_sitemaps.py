import requests

from lxml import etree
import xmltodict
from datetime import datetime
import logging
from typing import Iterable

import requests
from lxml.html import HtmlElement
import re

from dutch_news_scrapers.scraper import TextScraper, Scraper
from dutch_news_scrapers.tools import response_to_dom


class DHCentraalScraper(Scraper):
    DOMAIN = "https://www.denhaagcentraal.net"
    PUBLISHER = "Den Haag Centraal"
    TEXT_CSS = ".article.article p"
    SITEMAP_URL = "https://www.denhaagcentraal.net/sitemap_index.xml"
    COLUMNS = {"image_url": "url", "section": "keyword", "modified_date": "date"}

    def get_links(self) -> Iterable[str]:
        data = ["https://www.denhaagcentraal.net/post-sitemap4.xml"]
        for d in data:
            r = requests.get(d)
            raw = xmltodict.parse(r.text)
            docs = [
                {"url": r["loc"], "date": r["lastmod"]} for r in raw["urlset"]["url"]
            ]
            docs = sorted(docs, key=lambda doc: doc["date"], reverse=True)
            for doc in docs:
                print(doc)
                if doc["url"].startswith("https://www.denhaagcentraal.net/"):
                    yield doc

    def meta_from_dom(self, dom: HtmlElement) -> dict:
        meta = {
            m.get("property", m.get("name")): m.get("content")
            for m in dom.cssselect("meta")
        }
        tags = [v for (k, v) in meta.items() if k]
        date_string = meta["article:published_time"]
        format_string = "%Y-%m-%dT%H:%M:%S%z"
        date = datetime.strptime(date_string, format_string)
        art = dict(
            title=meta["og:title"],
            date=date,
        )
        if "article:modified_time" in meta:
            art["modified_date"] = meta["article:modified_time"]
        print(art)
        return art
