from dutch_news_scrapers.scraper import TextScraper


class OmroepFlevolandScraper(TextScraper):
    DOMAIN = "omroepflevoland.nl"
    PUBLISHER = "Omroep Flevoland"
    TEXT_CSS = ".article__content > p"
