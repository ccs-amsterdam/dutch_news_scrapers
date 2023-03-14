import requests

from lxml import etree
import xmltodict

import logging
from typing import Iterable
import datetime
import locale
import requests
from lxml.html import HtmlElement

from dutch_news_scrapers.scraper import TextScraper, Scraper
from dutch_news_scrapers.tools import response_to_dom

class StedenDriehoekScraper(Scraper):
    PAGES_URL = "https://www.stedendriehoek.nl/deventer/page/{page}"
    DOMAIN = "stedendriehoek.nl/deventer"
    PUBLISHER = "Stedendriehoek"
    TEXT_CSS = "div.content p"
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}


    def get_links(self) -> Iterable[str]:
        r = requests.get("https://www.stedendriehoek.nl/post-sitemap14.xml")
        raw = xmltodict.parse(r.text)
        urls = [r["loc"] for r in reversed(raw["urlset"]["url"])]
        for url in urls:
            if 'vacatures' in url:
                continue
            else:
                if url.startswith("https://www.stedendriehoek.nl/deventer") :
                    yield url

    def meta_from_dom(self, dom):
        article = {}
        headline = dom.cssselect("h1")
        if headline:
            article['title'] = headline[0].text_content()
        else:
            article['title'] = "no headline"
        tags = dom.cssselect("p.primary-category")
        article['tags'] = [" , ".join(t.text_content() for t in tags)]
        meta = dom.cssselect("div.flexbox-container.post-meta.margin-bottom p")
        meta = meta[0].text_content().split("op")
        author = meta[0]
        article['author'] = author.replace("Door","").replace("-","").strip()
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = meta[1].strip()
        article['date'] = datetime.datetime.strptime(date, "%d %b %Y").isoformat()
        return article

    def scrape_article(self, url: str) -> dict:
        logging.info(f"scraping article for {url}")
        r = requests.get(url)
        dom = response_to_dom(r)
        article = self.meta_from_dom(dom)
        if 'publisher' not in article and self.PUBLISHER:
            article['publisher'] = self.PUBLISHER
        article['text'] = self.text_from_dom(dom)
        if not article['text']:
            return
        if 'url' not in article:
            article['url'] = url
        if not article.get('text', '').strip():
            import json; print(json.dumps(article, indent=2, default=str))
            raise ValueError(f"Article {article['url']} has empty text {repr(article['text'])}!")
        for key in set(article.keys()) - {"date", "text", "title", "url"}:
            if article[key] is None:
                del article[key]
        return article

