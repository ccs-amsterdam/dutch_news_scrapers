import re
import datetime
import locale

from dutch_news_scrapers.scraper import TextScraper, Scraper
from dutch_news_scrapers.tools import response_to_dom


class StedenDriehoekScraper(Scraper):
    PAGES_URL = "https://www.stedendriehoek.nl/deventer/page/{page}"
    PAGES_RANGE = 20
    PAGE_START = 1
    DOMAIN = "stedendriehoek.nl/deventer"
    PUBLISHER = "Stedendriehoek"
    TEXT_CSS = "div.content p"
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}


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


    def get_links_from_dom(self, dom):
        links = list(dom.cssselect('div.container a'))
        for link in links:
            url = link.get("href")
            if 'tv-gids' in url:
                continue
            if re.match(r"https://www\.stedendriehoek\.nl/deventer/(zorg|politiek|sport|112|ondernemend|columns)/.", url):
                print(url)
                yield url


