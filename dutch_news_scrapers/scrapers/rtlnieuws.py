from dutch_news_scrapers.scraper import TextScraper


class RTLScraper(TextScraper):
    DOMAIN = "rtlnieuws.nl"
    PUBLISHER = "RTL.nl"
    TEXT_CSS = "div#sticky-parent p, h2"


