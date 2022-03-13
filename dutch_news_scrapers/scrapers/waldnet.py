from dutch_news_scrapers.scraper import TextScraper


class WaldnetScraper(TextScraper):
    DOMAIN = "waldnet.nl"
    PUBLISHER = "WâldNet"
    TEXT_CSS = ".kolom_haad > .artikel > p, .artikel h2"
