import xmltodict
from lxml import html
import re
import datetime
import locale
from typing import Iterable
import logging

import requests
from amcat4py import AmcatClient
from lxml.html import HtmlElement

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

class IndebuurtDeventer(Scraper):
    PUBLISHER = "Indebuurt Deventer"
    TEXT_CSS = "div.entry__content p, div.entry__content h2"
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "category": "keyword"
               }

    def get_links(self) -> Iterable[str]:
        r = requests.get("https://indebuurt.nl/deventer/post-sitemap8.xml")
        raw = xmltodict.parse(r.text)
        urls = [r["loc"] for r in reversed(raw["urlset"]['url'])]
        for url in urls:
            yield url

    def meta_from_dom(self, dom):
        article = {}
        try:
            section = dom.cssselect("p.entry__sponsor")
            section = section[0].text_content().strip()
            article['section'] = section.replace("Aangeboden door", "").strip()
        except IndexError as e:
            logging.warning(f"not sponsored: {e}")
        headline = dom.cssselect("h1.entry__title")
        if headline:
            article['title'] = headline[0].text_content()
        else:
            article['title'] = "no headline"
        meta = dom.cssselect("div.entry__meta li")
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = meta[0].text_content().strip()
        article['date'] = datetime.datetime.strptime(date, "%d %B %Y")
        article['author'] = meta[1].text_content().strip()
        if not article['author']:
            article['author'] = "gesponsord"
        tags = dom.cssselect("div.subjects a")
        tag = " , ".join(t.text_content() for t in tags)
        article['tags'] = tag
        return article



