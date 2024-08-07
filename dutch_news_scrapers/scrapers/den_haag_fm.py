from dutch_news_scrapers.scraper import TextScraper
from dutch_news_scrapers.scraper import TextScraper, Scraper
from dutch_news_scrapers.tools import response_to_dom
import requests
import lxml
import xmltodict
from typing import Iterable
import logging
from lxml.html import HtmlElement


class ArticleDoesNotExist(Exception):
    pass


def get_text(element):
    # Thanks https://stackoverflow.com/questions/18660382
    for br in element.xpath(".//br"):
        br.tail = "\n\n" + br.tail if br.tail else "\n\n"
    return element.text_content()


class DHFMScraper(Scraper):
    DOMAIN = "https://www.denhaagfm.nl"
    PUBLISHER = "Den Haag FM"
    TEXT_CSS = "div.layout-component div.text, h2"
    SITEMAP_URL = "https://www.denhaagfm.nl/sitemap/sitemap.xml.gz"

    def get_links(self) -> Iterable[str]:
        data = ["https://www.denhaagfm.nl/sitemap/sitemap-0.xml.gz"]
        for d in data:
            r = requests.get(d)
            raw = xmltodict.parse(r.text)
            docs = [{"url": r["loc"]} for r in raw["urlset"]["url"]]
            # docs = sorted(docs, key=lambda doc: doc["date"], reverse=True)
            for doc in docs:
                print(doc)
                if doc["url"].startswith("https://www.denhaagfm.nl/dhfm"):
                    yield doc
