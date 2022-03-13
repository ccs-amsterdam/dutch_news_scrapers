from dutch_news_scrapers.scraper import TextScraper


class BeatFMScraper(TextScraper):
    DOMAIN = "beatfm.nl"
    PUBLISHER = "Beat FM.nl"
    TEXT_CSS = ".article-content p"
