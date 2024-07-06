import os
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
from amcat4py import AmcatClient
from urllib.parse import urljoin
from dutch_news_scrapers.scraper import TextScraper, Scraper
from typing import Iterable
from PIL import Image
import locale


def clean(txt):
    pars = re.split(r"\s*\n\s*\n\s*", txt)
    pars = [re.sub("-\n(?!\n)", "", p) for p in pars]
    pars = [re.sub("\n(?!\n)", " ", p) for p in pars]
    cleaned = "\n\n".join(pars)
    return cleaned


def get_image_text(file, delete=True):
    d = Path(tempfile.mkdtemp())
    try:
        print(f"FILE IS {file}")
        img = Image.open(f"data/deventernieuws_tot/alleweken/{file}")
        img.save(d / "image.png")
        # logging.info(f"Converting to png")
        # subprocess.check_call(["inkscape", d/'image.jpg', "-d", "192", "-o", d/'image.png'], stderr=subprocess.DEVNULL)
        logging.info("Running tesseract OCR")
        subprocess.check_call(["tesseract", d / "image.png", d / "text"], stderr=subprocess.DEVNULL)
        text = (d / "text.txt").open().read()
        return clean(text)
    finally:
        if delete:
            rmtree(d, ignore_errors=True)


class Deventernieuws(Scraper):
    PUBLISHER = "DeventernieuwsPrint"
    # COLUMNS = {"krant": "url"}

    def scrape_article(self, file):
        art = {}
        text = get_image_text(file)
        # Take first sentence of first paragraph as title, rest as body
        paras = text.strip().split("\n\n")
        sentences = tokenize.sent_tokenize(paras[0])
        locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")
        ##parts = file.strip().split("-")
        # art['title']=parts[0]
        # date = parts[1]
        # print(f"DATE IS {date}")
        if not (m := re.match(r"(.*)-(\d+ \w+ \d{4})-p.(\d+).(png|PNG)", file.strip())):
            raise ValueError(f"Cannot parse title {file}")
        title, date, page, _ = m.groups()
        art["title"] = m.group(1)
        art["date"] = datetime.datetime.strptime(m.group(2), "%d %B %Y")
        art["page"] = int(m.group(3))
        art["publisher"] = self.PUBLISHER
        par1text = " ".join(sentences[1:])
        art["text"] = "\n\n".join([par1text] + paras[1:])
        print(f"ARTIKEL IS {art}")
        return art

    def scrape_articles(self, urls=None) -> Iterable[dict]:
        files = os.listdir("data/deventernieuws_tot/alleweken/")
        print(files)
        for file in files:
            print(f"FILE 0 is {file}")
            yield self.scrape_article(file)
