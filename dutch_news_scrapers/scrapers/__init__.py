import sys
from importlib import import_module
from inspect import getmembers, isclass
from pkgutil import iter_modules
from typing import Iterable
from urllib.parse import urlparse

from dutch_news_scrapers.scraper import TextScraper, Scraper


def get_all_scrapers() -> Iterable[type[TextScraper]]:
    """
    Return all scrapers in submodules of the .scrapers module
    """
    for m in iter_modules(sys.modules[__name__].__path__):
        module = import_module(f".{m.name}", __package__)
        for name, obj in getmembers(module):
            if isclass(obj) and issubclass(obj, TextScraper) and obj not in (TextScraper, Scraper):
                yield obj


def get_scraper_for_publisher(publisher: str):
    for scraper in get_all_scrapers():
        if scraper.PUBLISHER == publisher:
            return scraper
    raise ValueError(f"Could not find scraper for publisher {publisher}")


def get_scraper_for_url(url: str):
    domain = urlparse(url).netloc
    for scraper in get_all_scrapers():
        if scraper.DOMAIN and scraper.DOMAIN in domain:
            return scraper
    raise ValueError(f"Could not find scraper for domain {domain}")
