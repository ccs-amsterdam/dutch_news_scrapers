from dutch_news_scrapers.scraper import TextScraper


class RTLScraper(TextScraper):
    DOMAIN = "rtlnieuws.nl"
    PUBLISHER = "RTL Nieuws"
    TEXT_CSS = "div.css-19tp5d5 h3,p"


