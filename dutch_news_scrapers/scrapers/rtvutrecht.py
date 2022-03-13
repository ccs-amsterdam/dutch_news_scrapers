from dutch_news_scrapers.scraper import TextScraper


class RTVUtrechtScraper(TextScraper):
    DOMAIN = "rtvutrecht.nl"
    PUBLISHER = "RTV Utrecht"
    TEXT_CSS = ".text"
