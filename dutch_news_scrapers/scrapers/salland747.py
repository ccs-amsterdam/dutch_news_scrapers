import logging
import re
import datetime
import locale
from typing import Iterable

import requests
import xmltodict

from dutch_news_scrapers.scraper import TextScraper, Scraper, ArticleDoesNotExist
from dutch_news_scrapers.tools import response_to_dom, serialize

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}


class Salland747Scraper(Scraper):
    PAGES_URL = "https://www.salland747.nl/page/{page}"
    PAGES_RANGE = 20
    PAGE_START = 1
    DOMAIN = "salland747.nl"
    PUBLISHER = "Salland747"
    TEXT_CSS = "div.entry-content p, div.entry-content div.text,  div.entry-content div.wp-block, div.entry-content.mh-clearfix"
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}

    def get_links(self) -> Iterable[str]:
        r = requests.get(f"https://www.salland747.nl/wp-sitemap-posts-post-3.xml", headers=HEADERS)
        raw = xmltodict.parse(r.text)
        urls = [r["loc"] for r in reversed(raw["urlset"]["url"])]
        for url in urls:
            print(url)
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
        if not article['text']:
            article['text']="-"
        if 'url' not in article:
            article['url'] = url
        if not article.get('text', '').strip():
            import json; print(json.dumps(article, indent=2, default=serialize))
            raise ValueError(f"Article {article['url']} has empty text {repr(article['text'])}!")
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
        tags = dom.cssselect("span.entry-meta-categories a")
        article['tags'] = [" , ".join(t.text_content() for t in tags)]
        author = dom.cssselect("span.entry-meta-author a")
        article['author'] = author[0].text_content().strip()
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = dom.cssselect("span.entry-meta-date a")
        date = date[0].text_content().strip()
        article['date'] = datetime.datetime.strptime(date, "%d %B %Y").isoformat()
        return article





