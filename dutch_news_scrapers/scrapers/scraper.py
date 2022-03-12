import logging
from typing import Iterable, List, Optional, Any, Union, Tuple, Set

import requests
from lxml.html import Element, HtmlElement
from lxml import html
import re

from dutch_news_scrapers.tools import serialize


class ArticleDoesNotExist(Exception):
    pass

class Scraper:
    DOMAIN: str = None
    PUBLISHER: str = None
    PAGES_URL: str = None
    PAGES_RANGE = None
    PAGE_START: int = 0
    PAGE_STEP: int = 1

    def __init__(self, proxies: Optional[dict]=None):
        self.session = requests.session()
        if proxies:
            self.session.proxies.update(proxies)
        self.initialize()

    def initialize(self):
        """
        Optional function to initialize scraper, e.g. accepting cookies
        """
        pass

    def scrape_text(self, url: str) -> str:
        """
        Scrape text for a given url
        :param url:
        :return: the text of the article
        """
        page = self.session.get(url)
        page.raise_for_status()
        tree = html.fromstring(page.text)
        return self.text_from_html(tree)

    def scrape_articles(self, urls=None) -> Iterable[dict]:
        """
        Scrape all articles from this scraper
        :return: an iterable of article dictionaries including at least title, date, and text
        """
        if urls is None:
            urls = set()
        for url in self.get_links():
            if url in urls:
                continue
            urls.add(url)
            try:
                yield self.scrape_article(url)
            except ArticleDoesNotExist as e:
                logging.warning(f"Article {url} does not exist: {e}")

    def get_links(self) -> Iterable[str]:
        """
        Generates all links and optional extra metadata from e.g. newspaper front page
        Returns a iterable of dictionaries {"url": url, ...}
        """
        if self.PAGES_RANGE is None:
            raise Exception("Please specify PAGES_RANGE or override get_links")
        for page in range(self.PAGE_START, self.PAGES_RANGE, self.PAGE_STEP):
            # yield from self.get_links_from_page(page) # zelfde als for x in ... yield x
            logging.info(f"Scraping page {page}")
            yield from self.get_links_from_page(page)

    def get_links_from_page(self, page: int) -> Iterable[str]:
        """
        Get the links from a single page
        """
        if self.PAGES_URL is None:
            raise Exception("Please specify PAGES_URL")
        page = requests.get(self.PAGES_URL.format(page=page))
        page.raise_for_status()
        tree = html.fromstring(page.text)
        return self.get_links_from_html(tree)

    def get_links_from_html(self, tree: HtmlElement) -> Iterable[str]:
        """
        Get the links from a parsed HTML page
        :param tree: an lxml.Element representing the selected page
        :return:  an iterable of dictionaries {"url": url, ...}
        """
        raise NotImplementedError

    def scrape_article(self, url: str) -> dict:
        """
        Scrape the given article, returning a document dict that can e.g. be uploaded to AmCAT.
        If the article could not be scraped, raises an exception
        :param url: URL of the article
        :return: dict with all needed article fields
        """
        logging.info(f"scraping article for {url}")
        try:
            r = requests.get(url)
        except requests.HTTPError as err:
            if err.response.status_code in (403, 404, 410):
                raise ArticleDoesNotExist() from err
            raise
        r.raise_for_status()

        tree = html.fromstring(r.text)
        article = self.meta_from_html(tree)
        if 'publisher' not in article and self.PUBLISHER:
            article['publisher'] = self.PUBLISHER
        article['text'] = self.text_from_html(tree)
        if not article.get('text', '').strip():
            import json; print(json.dumps(article, indent=2, default=serialize))
            raise ValueError(f"Article {article['url']} has empty text {repr(article['text'])}!")
        for key in set(article.keys()) - {"date", "text", "title", "url"}:
            if article[key] is None:
                del article[key]
        return article

    def meta_from_html(self, html: HtmlElement) -> dict:
        """
        Scrape all relevant meta information from this article
        :param html: the parsed web page
        :return: dict with at least title and date keys
        """
        raise NotImplementedError()

    def text_from_html(self, html: HtmlElement) -> str:
        """
        Scrape the given article page, returning a completed dict (except for url) that can be uploaded to AmCAT.
        :param html: the parsed web page
        :return: the text of the article
        """
        raise NotImplementedError()