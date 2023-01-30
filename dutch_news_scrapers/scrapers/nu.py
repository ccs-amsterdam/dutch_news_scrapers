from dutch_news_scrapers.scraper import TextScraper


class NUScraper(TextScraper):
    DOMAIN = "nu.nl"
    PUBLISHER = "NU.nl"
    TEXT_CSS = "div.block-wrapper div.block-content > p"
