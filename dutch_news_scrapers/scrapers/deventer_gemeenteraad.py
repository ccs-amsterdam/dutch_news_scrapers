import amcat4py
import xmltodict
import datetime
from amcat4py import amcatclient
from amcat4py.amcatclient import AmcatClient
import requests
import re
import html
from dutch_news_scrapers.tools import upload_batches


def strip_html(s: str):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s*\n\s*\n", "\n\n", s)
    s = html.unescape(s)
    return s.strip()

def get_article(url):
    r = requests.get(url)
    raw = xmltodict.parse(r.text)
    articles = []
    for art in raw['news_archive']['news_item']:
        article={}
        article['title'] = art['title']
        preamble = art['preamble']
        text = preamble + art['body']
        article['text'] = strip_html(text)
        article['url'] = "https://gemeenteraad.deventer.nl/nieuws-van-de-gemeenteraad/archive.xml"
        date = art['published_at'].replace("+0200","").replace("+0100","").strip()
        article['date'] = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").isoformat()
        articles.append(article)
    return articles



url = "https://gemeenteraad.deventer.nl/nieuws-van-de-gemeenteraad/archive.xml"
arts = get_article(url)
conn = amcat4py.AmcatClient("http://localhost/amcat")
conn.delete_index("gemeenteraad_deventer")
conn.create_index("gemeenteraad_deventer")
conn.upload_documents(index="gemeenteraad_deventer", articles=arts)


