from amcat4py import AmcatClient

import requests
import cssselect
import argparse
import amcat4py
import re
from lxml import html
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}



def get_links(url):
    while True:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        tree = html.fromstring(r.text)
        hrefs = tree.cssselect("div.category- a")
        for href in hrefs:
            ref = href.get("href")
            yield dict(
                url = ref
            )
        onclick_attribute = tree.cssselect('button[onclick]')[0].get('onclick')
        next_url = re.search(r"loadMore\.GetHtml\(this, 'ArticleRow', '(.+?)'\);", onclick_attribute).group(1)
        url = f"https://www.rodi.nl/denhaag/components/html?component=ArticleRow&key={next_url}"

        

def get_article(art):
    url = f"https://www.rodi.nl{art}"
    if url.startswith("https://www.rodi.nl/denhaag/nieuws/"):
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        tree = html.fromstring(r.text)
        title = tree.cssselect("article h1")[0].text_content()
        date = tree.cssselect('time')[0].get('datetime')
        text = tree.cssselect("article p")
        text2 = "\n\n".join(t.text_content().strip() for t in text)
        yield dict(
                url = url,
                title=title,
                date=date,
                text=text2,
                publisher = "Rodi Den Haag"
            )
    else:
        return


    

parser = argparse.ArgumentParser()

parser.add_argument("server", help="AmCAT host name",)
parser.add_argument("index", help="AmCAT index")

args = parser.parse_args()

conn = AmcatClient(args.server)


url = "https://www.rodi.nl/denhaag"
for doc in get_links(url):
    url = doc['url']
    arts = get_article(url)
    for art in arts:
        conn.upload_documents(args.index, [art])
