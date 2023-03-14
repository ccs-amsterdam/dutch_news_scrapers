import re
import datetime
import locale

from dutch_news_scrapers.scraper import TextScraper, Scraper
from dutch_news_scrapers.tools import response_to_dom


class Salland1Scraper(Scraper):
    PAGES_URL = "https://www.salland1.nl/category/deventer/page/{page}"
    PAGES_RANGE = 20
    PAGE_START = 1
    DOMAIN = "salland1.nl"
    PUBLISHER = "Salland1"
   # TEXT_CSS = "div.tdb-block-inner p"
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}


    def meta_from_dom(self, dom):
        article = {}
        headline = dom.cssselect("h1.tdb-title-text")
        if headline:
            article['title'] = headline[0].text_content()
        else:
            article['title'] = "no headline"
        tags = dom.cssselect("div.tdb-category a")
        article['tags'] = [" , ".join(t.text_content() for t in tags)]
        author = dom.cssselect("a.tdb-author-name")
        author = author[0].text_content().strip()
        article['author'] = author.replace("Door","").replace("-","").strip()
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = dom.cssselect("time.entry-date")
        date = date[0].text_content().strip()
        article['date'] = datetime.datetime.strptime(date, "%d %B %Y").isoformat()
        return article


    def get_links_from_dom(self, dom):
        links = list(dom.cssselect('div#tdi_64 h3 a'))
        for link in links:
            url = link.get("href")
            if 'tv-gids' in url:
                continue
            print(url)
            yield url

    def text_from_dom(self, dom):
        body_ps = dom.cssselect('div.tdb-block-inner p,td')
        text = "\n\n".join(p.text_content() for p in body_ps).strip()
        if not text:
            text = "-"
        return text

