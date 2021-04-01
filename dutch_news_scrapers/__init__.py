from dutch_news_scrapers.scraper import Scraper
from dutch_news_scrapers.scrapers import ADScraper, NOSScraper, NUScraper, VKScraper, TELScraper, RTLScraper, \
    NRCScraper, TRWScraper

SCRAPERS = None


def all_scrapers(**kargs):
    global SCRAPERS
    if SCRAPERS is None:
        SCRAPERS = [ADScraper(**kargs),
            NOSScraper(**kargs),
            NUScraper(**kargs),
            VKScraper(**kargs),
            TELScraper(**kargs),
            RTLScraper(**kargs),
            NRCScraper(**kargs),
            TRWScraper(**kargs),
            ]
    return SCRAPERS
