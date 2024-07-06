

from lxml import etree
import datetime
from typing import Iterable
from lxml.html import HtmlElement
from scraper import TextScraper, Scraper
from tools import response_to_dom
import re



def fix_date(date):
    if date.endswith("Z"):
        date = re.sub("Z$", "", date)
        print(date)
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
    return date

class RTVOostSitemapScraper(Scraper):
    DOMAIN = "https://www.rtvoost.nl"
    PUBLISHER = "RTV Oost"
    TEXT_CSS = ".article-content div.text, .article-content h2"
    SITEMAP_URL = "https://www.rtvoost.nl/sitemap/sitemap.xml.gz"
    HEADERS = {'Accept': 'application/vnd.groei.overijssel+json;v=5.0',
               'X-Groei-Platform': 'web'}
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}
   
    
    def meta_from_dom(self, dom: HtmlElement) -> dict:
        meta = {m.get('data-hid'): m.get('content') for m in dom.cssselect("meta")}
        tags = [v for (k,v) in meta.items() if k and k.startswith("article:tag-")]
        art = dict(
            title = meta['og:title'],
            date = fix_date(meta['article:published_time']),
            section = meta['article:section'],
            image_url = meta['og:image'],
            tags = tags
        )
        if 'article:modified_time' in meta:
            art['modified_date'] = fix_date(meta['article:modified_time'])
            print(art)
            return art





