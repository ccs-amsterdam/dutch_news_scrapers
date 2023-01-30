from dutch_news_scrapers.scraper import TextScraper


class NOSScraper(TextScraper):
    DOMAIN = "nos.nl"
    PUBLISHER = "NOS.nl"
    TEXT_CSS = "p.text_3v_J6Y0G"
