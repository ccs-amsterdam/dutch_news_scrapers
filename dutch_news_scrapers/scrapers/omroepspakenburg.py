import datetime
import locale
from dutch_news_scrapers.scraper import Scraper


class OmroepSpakenburgScraper(Scraper):
    PAGES_URL = "https://www.omroepspakenburg.nl/category/nieuws/page/{page}"
    PAGES_RANGE = 200
    PAGE_START = 1
    PUBLISHER = 'omroepspakenburg'

    def meta_from_html(self, html):
        article = {}
        headline = html.cssselect("h1.entry-title")
        article['title'] = headline[0].text_content()
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = html.cssselect("span.td-post-date")
        date = date[0].text_content().strip()
        article['date'] = datetime.datetime.strptime(date, "%d %B %Y").isoformat()
        return article

    def text_from_html(self, html):
        body_ps = html.cssselect('div.td-ss-main-content')
        if not body_ps:
            body_ps = html.cssselect('div.td-post-content.tagdiv-type div')
        return "\n\n".join(p.text_content() for p in body_ps)

    def get_links_from_html(self, html):
        articles = list(html.cssselect('h3.entry-title'))
        for art in articles:
            links = art.cssselect("a")
            link = links[0].get("href")
            if 'tv-gids' in link:
                continue
            yield link
