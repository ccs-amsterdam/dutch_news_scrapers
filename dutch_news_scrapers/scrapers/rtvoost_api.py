from typing import Iterable

import requests
from lxml.html import HtmlElement

from dutch_news_scrapers.scraper import TextScraper, Scraper
from dutch_news_scrapers.tools import response_to_dom


class RTVOostScraper(Scraper):
    DOMAIN = "rtvoost.nl"
    PUBLISHER = "RTV Oost2"
    TEXT_CSS = ".article-content div.text, .article-content h2"
    API_URL = 'https://api.regiogroei.cloud/page/allenieuws?page=nieuws&id=allenieuws'
    HEADERS = {'Accept': 'application/vnd.groei.overijssel+json;v=5.0',
               'X-Groei-Platform': 'web'}
    COLUMNS = {"image_url": "url",
               "section": "keyword",
               "modified_date": "date"}

    def href_from_item(self, item):
        href = item['_links']['web']['href']
        return f"https://{self.DOMAIN}/{href}"

    def get_links(self) -> Iterable[str]:
        r = requests.get(self.API_URL, headers=self.HEADERS)
        r.raise_for_status()
        data = r.json()
        while True:
            next_url = None
            for component in data['components']:
                if component['type']  == "news-category-list":
                    for item in component['items']:
                        print(self.href_from_item(item))
                        #yield self.href_from_item(item)
                if component['type'] == "spotlight-header":
                    for item in component['slides']:
                        print(self.href_from_item(item))
                        #yield self.href_from_item(item)
                if component['type'] == "load-more":
                    next_url = component['_links']['next']['href']
            next_url = f"https://api.regiogroei.cloud{next_url}"
            print(f"----> {next_url}")
            r = requests.get(next_url, headers=self.HEADERS)
            r.raise_for_status()
            data = r.json()

    def get_video_url(self, item):
        """Resolve video url to actual article. Not used now since these articles are also in the regular stream"""
        url = self.href_from_item(item)
        r = requests.get(url)
        dom = response_to_dom(r)
        links = {a.text_content().strip(): a.get('href') for a in dom.cssselect("a.navigation-link")}
        href = links['Lees complete artikel']
        print(f"{url} -> {href}")
        return f"https://{self.DOMAIN}/{href}"

    def meta_from_dom(self, dom: HtmlElement) -> dict:
        meta = {m.get('data-hid'): m.get('content') for m in dom.cssselect("meta")}
        tags = [v for (k,v) in meta.items() if k and k.startswith("article:tag-")]
        return dict(
            title = meta['og:title'],
            date = meta['article:published_time'],
            modified_date = meta['article:modified_time'],
            section = meta['article:section'],
            image_url = meta['og:image'],
            tags = tags
        )




