import locale

import amcat4py
import xmltodict
import datetime
from amcat4py import amcatclient
from amcat4py.amcatclient import AmcatClient
import requests
import re
from lxml import html
from dutch_news_scrapers.tools import upload_batches

BASEURL = "https://www.deventer.nl/nieuws/2022/"


def get_page(pag):
    print(pag)
    url = f"{BASEURL}{pag}"
    print(f"URL IS {url}")
    page = requests.get(url)
    page.raise_for_status()
    tree = html.fromstring(page.text)
    return tree

def get_links(tree):
    links = tree.cssselect("div.news_items a")
    urls=[]
    for link in links:
        a = link.get("href")
        urls.append(a)
    return urls


def get_articles(pag):
    pagina = get_page(pag)
    links = get_links(pagina)
    articles = []
    for url in links:
        article={}
        page = requests.get(url)
        tree = html.fromstring(page.text)
        title = tree.cssselect("div.title h1")
        article['title']=title[0].text_content().strip()
        date = tree.cssselect("p.publicationDate")
        date = date[0].text_content().strip()
        date = date.replace("Publicatiedatum:", "").replace("om ","").strip()
        locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
        article['date'] = datetime.datetime.strptime(date, "%d %B %Y %H:%M").isoformat()
        text =  tree.cssselect("div.summary p, div.htmlField p, div.htmlField h2")
        text2 = "\n\n".join(t.text_content().strip() for t in text)
        article['text']= text2
        articles.append(article)
    print(articles)
    return articles


conn = amcat4py.AmcatClient("http://localhost/amcat")
conn.delete_index("gemeenteraad_nieuws")
conn.create_index("gemeenteraad_nieuws")
pages = range(8,12,1)
for pag in pages:
    arts = get_articles(pag)
    conn.upload_documents(index="gemeenteraad_nieuws", articles=arts)


