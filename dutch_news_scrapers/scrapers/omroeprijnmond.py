from dutch_news_scrapers.scraper import TextScraper


class OmroepRijnmondScraper(TextScraper):
    DOMAIN = "rijnmond.nl"
    PUBLISHER = "Omroep Rijnmond"
    TEXT_CSS = ".article-content div.text, .article-content h2"
