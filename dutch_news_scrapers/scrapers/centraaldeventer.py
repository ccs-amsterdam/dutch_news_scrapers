import logging
import re
import datetime
import locale
from typing import Iterable

import requests
import xmltodict

from dutch_news_scrapers.scraper import TextScraper, Scraper, ArticleDoesNotExist
from dutch_news_scrapers.tools import response_to_dom

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}


class CentraalDeventerScraper(Scraper):
    PAGES_URL = "https://www.centraaldeventer.nl/wp-sitemap.xml"
    PAGES_RANGE = 20
    PAGE_START = 1
    DOMAIN = "centraaldeventer.nl"
    PUBLISHER = "CentraalDeventer"
    TEXT_CSS = "div.entry-content p"
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}

    def get_links(self) -> Iterable[str]:
        pages = 4
        for p in pages:
            r = requests.get(f"https://www.centraaldeventer.nl/wp-sitemap-posts-post-{p}.xml", headers=HEADERS)
            raw = xmltodict.parse(r.text)
            urls = [r["loc"] for r in raw["urlset"]["url"]]
            for url in urls:
                if "https://www.centraaldeventer.nl/deventer-algemeen/welkom/" in url:
                    continue
                yield url

    def scrape_article(self, url: str) -> dict:
        logging.info(f"scraping article for {url}")
        r = requests.get(url, headers=HEADERS)
        if r.status_code in (403, 404, 410):
            raise ArticleDoesNotExist(f"HTTP {r.status_code}: {url}")
        dom = response_to_dom(r)
        article = self.meta_from_dom(dom)
        if 'publisher' not in article and self.PUBLISHER:
            article['publisher'] = self.PUBLISHER
        article['text'] = self.text_from_dom(dom)
        if article['text'] == " ":
            article['text']="-"
        if 'url' not in article:
            article['url'] = url
        for key in set(article.keys()) - {"date", "text", "title", "url"}:
            if article[key] is None:
                del article[key]
        return article

    def meta_from_dom(self, dom):
        article = {}
        headline = dom.cssselect("h1.entry-title")
        if headline:
            article['title'] = headline[0].text_content()
        else:
            article['title'] = "no headline"
        tags = dom.cssselect("div.post-meta p a[rel='tag']")
        article['tags'] = [" , ".join(t.text_content() for t in tags)]
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = dom.cssselect("span.updated")
        date = date[0].text_content().strip()
        article['date'] = datetime.datetime.strptime(date, "%d %b,%Y").isoformat()
        return article





