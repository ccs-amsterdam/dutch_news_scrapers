import datetime
import locale
from dutch_news_scrapers.scraper import Scraper


class OmroepAlmereScraper(Scraper):
    PAGES_URL = "https://omroepalmere.nl/category/almere/page/{page}"
    PAGES_RANGE = 200
    PAGE_START = 1
    PUBLISHER = 'Omroep Almere'
    DOMAIN = 'omroepalmere.nl'
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
        articles = list(dom.cssselect('h2.entry-title'))
        for art in articles:
            links = art.cssselect("a")
            link = links[0].get("href")
            if 'tv-gids' in link:
                continue
            yield link
