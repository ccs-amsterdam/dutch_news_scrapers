import datetime
import locale
from dutch_news_scrapers.scraper import Scraper


class ML5Scraper(Scraper):
    PAGES_URL = "https://www.ml5.nl/nieuws/page/{page}"
    PAGES_RANGE = 200
    PAGE_START = 1
    PUBLISHER = 'ML5'
    DOMAIN = 'ml5.nl'
    #COLUMNS = {'views': 'long'}

    def meta_from_dom(self, dom):
        article = {}
        headline = dom.cssselect("h1.entry-title")
        print(headline)
        if headline:
            article['title'] = headline[0].text_content()
        else:
            article['title'] = "no headline"
        tags = dom.cssselect("div.entry-meta")
        tag = " , ".join(t.text_content() for t in tags)
        article['tags'] = tag.strip()
        author = dom.cssselect("div.card-section div.mb-1")
        author = author[0].text_content()
        article['author'] = author.strip()
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = dom.cssselect("div.card-section div.mb-3")
        date = date[0].text_content().strip()
        article['date'] = datetime.datetime.strptime(date, "%d %B %Y").isoformat()
        return article

    def text_from_dom(self, dom):
        body_ps = dom.cssselect('entry-content clear > p')
        if not body_ps:
            body_ps = dom.cssselect('div.td-post-content.tagdiv-type div')
        text = "\n\n".join(p.text_content() for p in body_ps).strip()
        # Soms hebben spakenburg artikelen gewoon echt geen tekst,
        # bv https://www.omroepspakenburg.nl/2022/03/07/duifjes/
        if not text:
            return "-"
        return text

    def get_links_from_dom(self, dom):
        articles = list(dom.cssselect('div.uabb-blog-post-content h3'))
        for art in articles:
            links = art.cssselect("a")
            link = links.get("href")
            link = f"https://www.nieuwsuitnijmegen.nl/{link}"
            print(link)
            if 'tv-gids' in link:
                continue
            yield link
