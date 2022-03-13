from dutch_news_scrapers.scraper import TextScraper


class OmroepFryslanScraper(TextScraper):
    DOMAIN = "omropfryslan.nl"
    PUBLISHER = "Omrop Fryslan"
    TEXT_CSS = ".content p, .content h2"
