import html
import re
import datetime
import locale
from typing import Iterable
import logging

import requests
from amcat4apiclient import AmcatClient

from dutch_news_scrapers.scraper import TextScraper, Scraper, ArticleDoesNotExist
from dutch_news_scrapers.tools import response_to_dom, serialize

ITEMS = {"algemeen": ("opmerkelijk-704", "220"),
         "112": ("112-216", "221"),
         #"sport": ("217"),
           #"uit":("227"),
            #"zakelijk":("219"),
            #"blogs": ("222"),
         }


def strip_html(s: str):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s*\n\s*\n", "\n\n", s)
    s = html.unescape(s)
    return s.strip()


class HanzeStad(Scraper):
    PUBLISHER = "Hanzestad"
    COLUMNS = {"category": "keyword", "a_id": "long"}

    def scrape_articles(self, urls=None) -> Iterable[dict]:
        for category, (urlpart, nummer) in ITEMS.items():
            for p in range(0 , 33, 3):
                for a in self.get_article(p, category, urlpart, nummer):
                    if a['url'] not in urls:
                        yield a

    def get_articles(self, p, nummer):
        r = requests.post("https://www.hanzestad.nl/process.php",
                          data={'actie': 'get-more-news-ajax', 'categoryId': str(nummer), 'limitFrom': str(p), 'limitPer': '3'})
        yield r.json()

    def get_article(self, p, category, urlpart, nummer):
        arts  = self.get_articles(p, nummer)
        for art in arts:
            a = art[0]
            article={}
            article['category'] = category
            article['publisher'] = self.PUBLISHER
            article['title'] = a['titel']
            article['a_id'] = a['a_id']
            article['text'] = strip_html(a['content'])
            article['date'] = datetime.datetime.strptime(a['datum_van'], "%Y-%m-%d %H:%M:%S")
            article['url'] = f"https://www.hanzestad.nl/artikel/{urlpart}/{nummer}/{a['url']}/{a['a_id']}/"
            #import json; print(json.dumps(article, indent=2, default=str))
            yield article


