import logging
import re
import datetime
import locale
from typing import Iterable
from lxml import html
import requests
import xmltodict
import dateparser
from dutch_news_scrapers.scraper import TextScraper, Scraper, ArticleDoesNotExist
from dutch_news_scrapers.tools import response_to_dom

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}


class WeltschmerzScraper(Scraper):
    PAGES_URL = "https://cafeweltschmerz.nl/overzicht/?sf_data=results&post_types=post&sf_paged={page}"
    PAGES_RANGE = 134
    PAGE_START = 1
    DOMAIN = "cafeweltschmerz.nl"
    PUBLISHER = "Cafeweltschmerz"
    TEXT_CSS = "div.content.py-5 p"
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}
   
    def get_links(self) -> Iterable[str]:
        if self.PAGES_RANGE is None:
            raise Exception("Please specify PAGES_RANGE or override get_links")
        for page in range(self.PAGE_START, self.PAGES_RANGE, self.PAGE_STEP):
            logging.info(f"Scraping page {page}")
            yield from self.get_links_from_page(page)


    def get_links_from_dom(self, dom):
        articles = list(dom.cssselect('div#theloop div.inner > a'))
        for art in articles:
            links = art.cssselect("a")
            link = links[0].get("href")
            yield link

    def meta_from_dom(self, dom):
        article = {}
        headline = dom.cssselect("h1")
        if headline:
            article['title'] = headline[0].text_content()
        else:
            article['title'] = "no headline"
        author = dom.cssselect("li.author")
        article['author'] = author[0].text_content().strip()
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = dom.cssselect("li.date")
        date = date[0].text_content().strip()
        if 'geleden in date':
            dt = dateparser.parse(date)
            article['date']=dt.strftime("%Y-%m-%d")
        else:
            article['date'] = datetime.datetime.strptime(date, "%d/%m/%Y").isoformat()
        return article


    def scrape_article(self, url: str) -> dict:
            logging.info(f"SCRAPING article for {url}")
            r = requests.get(url, headers=HEADERS)
            if r.status_code in (403, 404, 410):
                raise ArticleDoesNotExist(f"HTTP {r.status_code}: {url}")
            dom = response_to_dom(r)
            article = self.meta_from_dom(dom)
            if 'publisher' not in article and self.PUBLISHER:
                article['publisher'] = self.PUBLISHER
            tags = dom.cssselect("div.general-tag-list.mb-5 li a")
            article['tags']= " , ".join(t.text_content() for t in tags)
            article['text'] = self.text_from_dom(dom)
            if article['text'] == " ":
                article['text']="-"
            if 'url' not in article:
                article['url'] = url
            for key in set(article.keys()) - {"date", "text", "title", "url"}:
                if article[key] is None:
                    del article[key]
            return article



