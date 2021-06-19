from dutch_news_scrapers.scraper import Scraper
from dutch_news_scrapers.scrapers import *

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
            OmroepFlevolandScraper(**kargs),
            OmroepGelderlandScraper(**kargs),
            OmroepZeelandScraper(**kargs),
            OmroepRijnmondScraper(**kargs),
            RTVUtrechtScraper(**kargs),
            RTVOostScraper(**kargs),
            NHNieuwsScraper(**kargs),
            LimburgScraper(**kargs),
            OmroepBrabantScraper(**kargs),
            OmroepFryslanScraper(**kargs),
            AT5Scraper(**kargs),
            RTVDrentheScraper(**kargs),
            OmroepWestScraper(**kargs)
                    ]
    return SCRAPERS
