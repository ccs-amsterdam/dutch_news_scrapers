import requests

from lxml import etree
import xmltodict
import locale
import dateparser
import logging
from typing import Iterable
import datetime
import requests
from lxml.html import HtmlElement

from dutch_news_scrapers.scraper import TextScraper, Scraper
from dutch_news_scrapers.tools import response_to_dom


class BlckBxScraper(Scraper):
    DOMAIN = "blckbx.tv"
    PUBLISHER = "Blckbx"
    TEXT_CSS = ".article-content div.text, .article-content h2"
    HEADERS = {'Accept': 'application/vnd.groei.overijssel+json;v=5.0',
               'X-Groei-Platform': 'web'}
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}
    CONTINUE_ON_ERROR = True



    def get_links(self) -> Iterable[dict]:
        r = requests.get("https://www.blckbx.tv/sitemaps-1-section-articles-1-sitemap.xml")
        raw = xmltodict.parse(r.text)
        arts= raw["urlset"]["url"]
        for art in arts:
            date= art["lastmod"]
            print(date)
            date = date.split("T")[0]
            print(date)
            date = datetime.datetime.strptime(date, "%Y-%m-%d").isoformat()
            url = art['loc']
            if not url.startswith(("https://www.blckbx.tv/binnenland/", "https://www.blckbx.tv/buitenland/", "https://www.blckbx.tv/economie/", "https://www.blckbx.tv/corona/",
                                "https://www.blckbx.tv/gezondheid", "https://www.blckbx.tv/klimaat", "https://www.blckbx.tv/tech-media")):
                continue
            else:
                yield dict(url=url, date=date)


    def meta_from_dom(self, dom: HtmlElement) -> dict:
        article = {}
        headline = dom.cssselect("h1")
        if headline:
            article['title'] = headline[0].text_content()
        else:
            article['title'] = "no headline"
        author = dom.cssselect("div.flex.flex-col.space-y-1")
        article['author'] = author[0].text_content().strip()
        return article


    def text_from_dom(self, dom: HtmlElement) -> str:
        intro = dom.cssselect("div.intro-body-text")
        intro = intro[0].text_content()
        texts = dom.cssselect("div.text-base")
        text = "\n\n".join(p.text_content() for p in texts)
        return text
    
    def scrape_article(self, url: str) -> dict:
        logging.info(f"SCRAPING article for {url}")
        r = requests.get(url)
        dom = response_to_dom(r)
        article = self.meta_from_dom(dom)
        if 'publisher' not in article and self.PUBLISHER:
            article['publisher'] = self.PUBLISHER
        article['text'] = self.text_from_dom(dom)
        if 'url' not in article:
            article['url'] = url
        if not article.get('text', '').strip():
            raise ValueError(f"Article {article['url']} has empty text {repr(article['text'])}!")
        for key in set(article.keys()) - {"date", "text", "title", "url"}:
            if article[key] is None:
                del article[key]       
        return article





