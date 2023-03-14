import requests
from urllib.request import urlretrieve
import tempfile 
import subprocess
import logging
from pathlib import Path
from shutil import rmtree
from lxml import html
import re
from lxml.html import HtmlElement
import re
from nltk import tokenize
import datetime
from datetime import date
from datetime import datetime
from amcat4py import AmcatClient
from urllib.parse import urljoin
from dutch_news_scrapers.scraper import Scraper
from typing import Iterable


#from dutch_news_scrapers.tools import response_to_dom


 #PAGE_URL = "https://indd.adobe.com/view/publication/36659e66-d103-49b2-968e-3e09b83b43c2/1"
    #url = "https://indd.adobe.com/view/publication/36659e66-d103-49b2-968e-3e09b83b43c2/1/publication-web-resources/image/{i}.svgz"
    
#from dutch_news_scrapers.scraper import TextScraper, Scraper, ArticleDoesNotExist
#from dutch_news_scrapers.tools import response_to_dom, serialize




def clean(txt):
        pars = re.split(r"\s*\n\s*\n\s*", txt)
        pars = [re.sub("-\n(?!\n)", "", p) for p in pars]
        pars = [re.sub("\n(?!\n)", " ", p) for p in pars]
        cleaned =  "\n\n".join(pars)
        return cleaned


def get_image_text(url, delete=True):
    d = Path(tempfile.mkdtemp())
    try:
        logging.info(f"Downloading {url} to {d}")
        urlretrieve(url, d/"image.svg")
        logging.info(f"Converting to png")
        subprocess.check_call(["inkscape", d/"image.svg", "-d", "192", "-o", d/"image.png"], stderr=subprocess.DEVNULL)
        logging.info("Running tesseract OCR")
        subprocess.check_call(["tesseract", d/"image.png", d/"text"], stderr=subprocess.DEVNULL)
        text = (d/"text.txt").open().read()
        return clean(text)
    finally:
        if delete:
            rmtree(d, ignore_errors=True)

def encoding_from_html(tree: HtmlElement):
    for m in tree.cssselect("meta"):
        content = m.get('content')
        if m.get("http-equiv") == "Content-Type" and 'charset' in content:
            if match := re.search("charset=([^;]+)", content):
                return match.group(1)


class BathmenseScraper(Scraper):
    PUBLISHER = "BathmenseKrantPrint"
    BASE_URL = "https://bathmensekrant.nl/uitgaves-print/"
    COLUMNS = {"krant": "url"}


    def get_editions(self):
        r = requests.get(self.BASE_URL)
        tree = html.fromstring(r.text)
        links = tree.cssselect("article.art-post li a")
        for link in links:
            url = link.get("href")
            text = link.text_content()
            if not "2023" in text:
                continue
            datum = text.split(" ")
            d1 = datum[-1]
            d2 = datum[-2]
            datum2 = f"{d1}-{d2}-3"
            print(f"DATUM={datum2}")
            datum4 = datetime.strptime(datum2, "%Y-%W-%w")
            print(f"DATUM is nu={datum4}")
            if url.startswith("//indd.adobe.com"):
                url = f"https:{url}"
            if url.startswith("https://indd.adobe.com/view/"):
                yield url, datum4
        
   
    def response_to_dom(self, response) -> HtmlElement:
        response.raise_for_status()
        dom = html.fromstring(response.text)
        enc = encoding_from_html(dom)
        if enc and response.encoding != enc:
            logging.warning(f"Switching encoding to {enc}")
            response.encoding = enc
            dom = html.fromstring(response.text)
        return dom


    def scrape_edition(self, base_url, datum):
        r = requests.get(base_url)
        r.raise_for_status()
        text = r.content
        if not (m := re.search(r'"VERSION_PREFIX":"?(\w+)"?}', r.text)):
            raise Exception(f"Cannot get version from {base_url}")
        version = m.group(1)

        view_url = base_url.replace("/view/", "/view/publication/")
        
        for page in range(20):        
            url = f"{view_url}/{version}/publication-{page}.html" if page else f"{view_url}/1/publication.html"
            r = requests.get(url)
            if r.status_code == 404:
                break
            dom = self.response_to_dom(r)
            for img in dom.cssselect("img"):
                if img.get('type') != 'image/svg+xml':
                    continue 
                img_url = urljoin(url, img.get('src'))
                yield dict(url=img_url, krant=url, date=datum)

    def scrape_article(self, img_url):
        art = {}
        text = get_image_text(img_url)
        # Take first sentence of first paragraph as title, rest as body
        paras = text.strip().split("\n\n")
        sentences = tokenize.sent_tokenize(paras[0])
        art['title']=sentences[0]
        art['publisher'] = self.PUBLISHER
        par1text = " ".join(sentences[1:])
        art['text'] = "\n\n".join([par1text] + paras[1:])
        return art

    def get_links(self, urls=None) -> Iterable[dict]:
        for url, datum in self.get_editions():
            print(url, datum)
            for article in self.scrape_edition(url, datum):
                yield article

