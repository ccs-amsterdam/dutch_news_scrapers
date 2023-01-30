import datetime
import locale
from dutch_news_scrapers.scraper import Scraper
from typing import Iterable, Optional
import requests
from dutch_news_scrapers.tools import serialize, response_to_dom


class ViaRoermondScraper(Scraper):
    PAGES_URL = "https://epapers.beeinmedia.nl/VIA/edities/roermond.html"
    PUBLISHER = 'VIA Roermond'
    DOMAIN = 'viaroermond.nl'
    #COLUMNS = {'views': 'long'}
    TEXT_CSS = 'div.entry-content > h2,div.entry-content > p'

    def meta_from_dom(self, dom):
        article = {}
        headline = dom.cssselect("h1.entry-title")
        if headline:
            article['title'] = headline[0].text_content()
        else:
            article['title'] = "no headline"
        tags = dom.cssselect("span.meta-item.cat-labels")
        tag = " , ".join(t.text_content() for t in tags)
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = dom.cssselect("time.entry-date.published")
        date = date[0].text_content().strip()
        article['date'] = datetime.datetime.strptime(date, "%d %B %Y").isoformat()
        return article

    def get_links_from_dom(self, dom):
        articles = list(dom.cssselect('a.epaper_editie'))
        print(articles)
        for art in articles:
            links = art.cssselect("a")
            link = links[0].get("href")
            if 'tv-gids' in link:
                continue
            yield link


    def get_links_from_page(self, page: int) -> Iterable[str]:
        """
        Get the links from a single page
        """
        if self.PAGES_URL is None:
            raise Exception("Please specify PAGES_URL")
        page = requests.get(self.PAGES_URL.format(page=page))
        dom = response_to_dom(page)
        return self.get_links_from_dom(dom)