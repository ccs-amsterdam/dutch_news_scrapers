import datetime
import locale
from dutch_news_scrapers.scraper import Scraper
import re

class AlmereNieuwsScraper(Scraper):
    PAGES_URL = "https://www.almere-nieuws.nl/nieuws/?page={page}"
    PAGES_RANGE = 200
    PAGE_START = 1
    PUBLISHER = 'Almere Nieuws'
    DOMAIN = 'almere-nieuws.nl'
    #COLUMNS = {'views': 'long'}
    TEXT_CSS = 'div.content-inner > h3,div.content-inner > p'

    def meta_from_dom(self, dom):
        article = {}
        headline = dom.cssselect("h3.heroflow__heading")
        if headline:
            article['title'] = headline[0].text_content().strip()
        else:
            article['title'] = "no headline"
        tag = dom.cssselect("p.heroflow__subheading.headingS > span")
        tag = tag[-1].text_content()
        article['tags'] = tag.strip()
        author1 = dom.cssselect("div.jeg_meta_author > a")
        author = author1[0].text_content().strip()
        article['author'] = author.replace("Gepubliceerd door","").replace("-","").strip()
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        datetext = dom.cssselect("span div.jeg_meta_author")
        if not datetext:
            datetext = dom.cssselect("div.meta_left div.jeg_meta_author")
        datetext1 = datetext[0].text_content()
        print(f"DATUM IS {datetext1}")
        datum = re.search('op ([\w\.-]+dag [\d{2}].*)', datetext1)
        datum = datum.group(1).strip()
        article['date'] = datetime.datetime.strptime(datum, "%A %d %B %Y om %H.%M uur").isoformat()
        print(article)
        return article


    def get_links_from_dom(self, dom):
        articles = list(dom.cssselect('h3.jeg_post_title'))
        print(articles)
        for art in articles:
            links = art.cssselect("a")
            link = links[0].get("href")
            link = f"https://almere-nieuws.nl{link}"
            print(f"link is {link}")
            if 'tv-gids' in link:
                continue
            if not "https://almere-nieuws.nl/nieuws" in link:
                continue
            yield link
