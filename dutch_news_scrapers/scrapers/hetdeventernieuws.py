
import datetime
import locale
import logging
import requests
from typing import Iterable
import xmltodict
from lxml import html
from dutch_news_scrapers.scraper import TextScraper, Scraper

from dutch_news_scrapers.tools import response_to_dom
from fake_useragent import UserAgent
import time

HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

def get_retry(url, **kargs):
    while True:
        try:
            logging.info(f"GET {url}")
            return requests.get(url, headers=HEADERS, **kargs)
        except ConnectionError as e:
            logging.warning(f"ConnectionError on getting {url}: {e}")
            time.sleep(10)

class DeventerNieuwsSitemapScraper(Scraper):
    PAGES_URL = "https://www.hetdeventernieuws.nl/nieuws/page/{page}/"
    PAGES_RANGE = 4
    PAGE_START = 2
    DOMAIN = "hetdeventernieuws.nl"
    PUBLISHER = "Het Deventer Nieuws"
    TEXT_CSS = "div.art-postcontent p"
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}
                

    def get_links(self) -> Iterable[str]:
        r = requests.get("https://www.hetdeventernieuws.nl/post-sitemap9.xml", headers=HEADERS)
        raw = xmltodict.parse(r.text)
        urls = [r["loc"] for r in reversed(raw["urlset"]["url"])]
        for url in urls:
            print(url)
            yield url
       

    def meta_from_dom(self, dom):
        article = {}
        headline = dom.cssselect("h1.entry-title")
        if headline:
            article['title'] = headline[0].text_content()
        else:
            article['title'] = "no headline"
        tags = dom.cssselect("ul.td-category")
        article['tags'] = [" , ".join(t.text_content() for t in tags)]
        author = dom.cssselect("div.td-author-by")
        author = author[0].text_content()
        article['author'] = author.replace("Door","").replace("-","").strip()
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = dom.cssselect("span.td-post-date")
        date = date[0].text_content().strip()
        article['date'] = datetime.datetime.strptime(date, "%d %B %Y")
        return article

    def text_from_dom(self, dom):
        body_ps = dom.cssselect('div.td-post-content p')
        text = "\n\n".join(p.text_content() for p in body_ps).strip()
        if not text:
            return "-"
        return text


    def get_links_from_dom(self, dom):
        links = list(dom.cssselect('div.td-ss-main-content h3 a'))
        for link in links:
            url = link.get("href")
            if 'tv-gids' in url:
                continue
            print(url)
            yield url


    def scrape_article(self, url: str) -> dict:
        r = get_retry(url)
        dom = response_to_dom(r)
        article = self.meta_from_dom(dom)
        if 'publisher' not in article and self.PUBLISHER:
            article['publisher'] = self.PUBLISHER
        article['text'] = self.text_from_dom(dom)
        if 'url' not in article:
            article['url'] = url
        if not article.get('text', '').strip():
            import json; print(json.dumps(article, indent=2, default=str))
            raise ValueError(f"Article {article['url']} has empty text {repr(article['text'])}!")
        for key in set(article.keys()) - {"date", "text", "title", "url"}:
            if article[key] is None:
                del article[key]
        return article

