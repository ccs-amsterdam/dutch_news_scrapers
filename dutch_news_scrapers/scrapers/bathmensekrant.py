
import datetime
import locale

from dutch_news_scrapers.scraper import TextScraper, Scraper
from dutch_news_scrapers.tools import response_to_dom


class BathmenseScraper(Scraper):
    PAGES_URL = "https://bathmensekrant.nl/page/{page}"
    PAGES_RANGE = 10
    PAGE_START = 1
    DOMAIN = "bathmense.nl"
    PUBLISHER = "Bathmense Krant"
    TEXT_CSS = "div.art-postcontent p"
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}



    def meta_from_dom(self, dom):
        article = {}
        headline = dom.cssselect("h1.art-postheader.entry-title")
        print(f"headline is {headline}")
        if headline:
            article['title'] = headline[0].text_content()
        else:
            article['title'] = "no headline"
        author = dom.cssselect("span.author.vcard")
        author = author[0].text_content()
        article['author'] = author.replace("Door","").replace("-","").strip()
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        date = dom.cssselect("span.entry-date.updated")
        date = date[0].text_content().strip()
        article['date'] = datetime.datetime.strptime(date, "%d %B %Y").isoformat()
        return article

    def text_from_dom(self, dom):
        body_ps = dom.cssselect('div.art-postcontent > p')
        text = "\n\n".join(p.text_content() for p in body_ps).strip()
        if not text:
            return "-"
        return text


    def get_links_from_dom(self, dom):
        links = list(dom.cssselect('div.art-content h2 a'))
        for link in links:
            url = link.get("href")
            if 'tv-gids' in url:
                continue
            print(url)
            yield url


