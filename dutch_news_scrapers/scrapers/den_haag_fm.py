from dutch_news_scrapers.scraper import TextScraper


class RTLScraper(TextScraper):
    DOMAIN = "https://www.denhaagfm.nl"
    PUBLISHER = "Den Haag FM"
    TEXT_CSS = "div.layout-component div.text, h2"


