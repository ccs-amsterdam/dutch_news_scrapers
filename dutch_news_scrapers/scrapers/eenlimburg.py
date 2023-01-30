from dutch_news_scrapers.scraper import TextScraper


class EenLimburgScraper(TextScraper):
    DOMAIN = "1limburg.nl"
    PUBLISHER = "1Limburg.nl"
    TEXT_CSS = ".node-article .article-lead, .node-article .article-body p"

