from inspect import isclass

from .omroepspakenburg import OmroepSpakenburgScraper
from .scraper import Scraper
from .scrapers import *


def get_all_scrapers():
    for obj in globals().values():
        if isclass(obj) and issubclass(obj, Scraper):
            yield obj


def get_scraper_for_publisher(publisher: str):
    for scraper in get_all_scrapers():
        if scraper.PUBLISHER == publisher:
            return scraper
    raise ValueError(f"Could not find scraper for publisher {publisher}")
