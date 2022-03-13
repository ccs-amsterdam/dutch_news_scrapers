from dutch_news_scrapers.scraper import TextScraper


class RTVOostScraper(TextScraper):
    DOMAIN = "rtvoost.nl"
    PUBLISHER = "RTV Oost"
    TEXT_CSS = ".article-content div.text, .article-content h2"
