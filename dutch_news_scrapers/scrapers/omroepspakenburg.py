import datetime
import locale
from dutch_news_scrapers.scraper import Scraper


class OmroepSpakenburgScraper(Scraper):
    PAGES_URL = "https://www.omroepspakenburg.nl/category/nieuws/page/{page}"
    PAGES_RANGE = 200
    PAGE_START = 1
    PUBLISHER = 'omroepspakenburg'
    DOMAIN = 'omroepspakenburg.nl'
    COLUMNS = {'views': 'long'}

    def meta_from_dom(self, dom):
        article = {}
        headline = dom.cssselect("h1.entry-title")
        if headline:
            article['title'] = headline[0].text_content()
        else:
            article['title'] = "no headline"
        tags = dom.cssselect("li.entry-category")
        tag = " , ".join(t.text_content() for t in tags)
        article['tags'] = tag
        author = dom.cssselect("div.td-post-author-name")
        author = author[0].text_content()
        article['author'] = author.replace("Door","").replace("-","").strip()
        views = dom.cssselect("div.td-post-views")
        article['views'] = int(views[0].text_content())
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = dom.cssselect("span.td-post-date")
        date = date[0].text_content().strip()
        article['date'] = datetime.datetime.strptime(date, "%d %B %Y").isoformat()
        return article

    def text_from_dom(self, dom):
        body_ps = dom.cssselect('div.td-post-content p')
        if not body_ps:
            body_ps = dom.cssselect('div.td-post-content.tagdiv-type div')
        text = "\n\n".join(p.text_content() for p in body_ps).strip()
        # Soms hebben spakenburg artikelen gewoon echt geen tekst,
        # bv https://www.omroepspakenburg.nl/2022/03/07/duifjes/
        if not text:
            return "-"
        return text

    def get_links_from_dom(self, dom):
        articles = list(dom.cssselect('h3.entry-title'))
        for art in articles:
            links = art.cssselect("a")
            link = links[0].get("href")
            if 'tv-gids' in link:
                continue
            yield link
