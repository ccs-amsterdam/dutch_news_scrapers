from dutch_news_scrapers.scraper import TextScraper


class RTLScraper(TextScraper):
    DOMAIN = "https://www.denhaagfm.nl"
    PUBLISHER = "Dagblad070"
    TEXT_CSS = "div.zm-post-content > p"


