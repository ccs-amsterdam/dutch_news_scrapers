import amcat4py
import xmltodict
import datetime
from amcat4py import amcatclient
from amcat4py.amcatclient import AmcatClient
import requests
import re
from lxml import html
from dutch_news_scrapers.tools import upload_batches


BASEURL = "https://zoek.officielebekendmakingen.nl/resultaten?svel=Publicatiedatum&svol=Aflopend&pg=10&q=(c.product-area==%22officielepublicaties%22)and((((w.organisatietype==%22gemeente%22)and(dt.creator==%22Deventer%22))))and(((w.publicatienaam==%22Tractatenblad%22))or((w.publicatienaam==%22Staatsblad%22))or((w.publicatienaam==%22Staatscourant%22))or((w.publicatienaam==%22Gemeenteblad%22))or((w.publicatienaam==%22Provinciaal%20blad%22))or((w.publicatienaam==%22Waterschapsblad%22))or((w.publicatienaam==%22Blad%20gemeenschappelijke%20regeling%22)))&zv=&col=AlleBekendmakingen&pagina="
ART_URL="https://zoek.officielebekendmakingen.nl/"


def strip_html(s: str):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s*\n\s*\n", "\n\n", s)
    s = html.unescape(s)
    return s.strip()


def get_page(pag):
    print(pag)
    url = f"{BASEURL}{pag}"
    print(f"URL IS {url}")
    page = requests.get(url)
    page.raise_for_status()
    tree = html.fromstring(page.text)
    return tree

def get_links(tree):
    links = tree.cssselect("div.Publicaties h2.result--title a")
    urls=[]
    for link in links:
        a = link.get("href")
        urls.append(a)
    return urls



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


pages = range(1,107,1)
for p in pages:
    tree = get_page(p)
    links = get_links(tree)

#conn = amcat4py.AmcatClient("http://localhost/amcat")
#conn.delete_index("gemeenteraad_deventer")
#conn.create_index("gemeenteraad_deventer")
#conn.upload_documents(index="gemeenteraad_deventer", articles=arts)


