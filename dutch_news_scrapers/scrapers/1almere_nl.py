import datetime
import locale
from dutch_news_scrapers.scraper import Scraper


class EenAlmere_nlScraper(Scraper):
    PAGES_URL = "https://www.1almere.nl/category/nieuws-almere/page/{page}"
    PAGES_RANGE = 200
    PAGE_START = 1
    PUBLISHER = '1almere.nl'
    DOMAIN = '1almere.nl'
    #COLUMNS = {'views': 'long'}

    def meta_from_dom(self, dom):
        article = {}
        headline = dom.cssselect("h1.is-title.post-title")
        if headline:
            article['title'] = headline[0].text_content()
        else:
            article['title'] = "no headline"
        tags = dom.cssselect("span.meta-item.cat-labels")
        tag = " , ".join(t.text_content() for t in tags)
        article['tags'] = tag.strip()
        author = dom.cssselect("span.meta-item.post-author")
        author = author[0].text_content()
        article['author'] = author.replace("By","").replace("-","").strip()
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = dom.cssselect("span.meta-item.date")
        date = date[0].text_content().strip()
        article['date'] = datetime.datetime.strptime(date, "%d %B %Y").isoformat()
        return article

    def text_from_dom(self, dom):
        body_ps = dom.cssselect('div.post-content.cf.entry-content.content-normal p')
        if not body_ps:
            body_ps = dom.cssselect('div.td-post-content.tagdiv-type div')
        text = "\n\n".join(p.text_content() for p in body_ps).strip()
        # Soms hebben spakenburg artikelen gewoon echt geen tekst,
        # bv https://www.omroepspakenburg.nl/2022/03/07/duifjes/
        if not text:
            return "-"
        return text

    def get_links_from_dom(self, dom):
        articles = list(dom.cssselect('h2.is-title.post-title'))
        for art in articles:
            links = art.cssselect("a")
            link = links[0].get("href")
            if 'tv-gids' in link:
                continue
            yield link
