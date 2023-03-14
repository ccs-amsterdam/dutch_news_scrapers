import html
import re
import datetime
import locale
from typing import Iterable
import logging
import itertools
import requests
from amcat4py import AmcatClient

from dutch_news_scrapers.scraper import TextScraper, Scraper, ArticleDoesNotExist
from dutch_news_scrapers.tools import response_to_dom, serialize

ITEMS = {"algemeen": ("opmerkelijk-704", "220"),
         "112": ("112-216", "221"),
         "sport": ("sport-948","217"),
          "uit":("uit-303","227"),
            "zakelijk":("zakelijk-573","219"),
            "blogs": ("blogs-395","222"),
         }


def strip_html(s: str):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s*\n\s*\n", "\n\n", s)
    s = html.unescape(s)
    return s.strip()


class HanzeStad(Scraper):
    PUBLISHER = "Hanzestad"
    COLUMNS = {"category": "keyword", "a_id": "long"}

    def scrape_category(self, urls, category, urlpart, nummer):
        for p in itertools.count(0, step=3):
            for a in self.get_article(p, category, urlpart, nummer):
                if a['url'] not in urls:
                    print(a['title'], a['date'])
                    yield a

    def scrape_articles(self, urls=None) -> Iterable[dict]:
        for category, (urlpart, nummer) in ITEMS.items():
            yield from self.scrape_category(urls, category, urlpart, nummer)

    def get_articles(self, p, nummer):
        r = requests.post("https://www.hanzestad.nl/process.php",
                          data={'actie': 'get-more-news-ajax', 'categoryId': str(nummer), 'limitFrom': str(p), 'limitPer': '3'})
        return r.json()

    def get_article(self, p, category, urlpart, nummer):
        arts  = list(self.get_articles(p, nummer))
        for art in arts:
            article={}
            article['category'] = category
            article['publisher'] = self.PUBLISHER
            article['title'] = art['titel']
            article['a_id'] = art['a_id']
            article['text'] = strip_html(art['content'])
            article['date'] = datetime.datetime.strptime(art['datum_van'], "%Y-%m-%d %H:%M:%S")
            article['url'] = f"https://www.hanzestad.nl/artikel/{urlpart}/{nummer}/{art['url']}/{art['a_id']}/"
            #import json; print(json.dumps(article, indent=2, default=str))
            yield article


