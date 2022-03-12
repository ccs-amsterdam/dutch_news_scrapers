import json
import logging
import sys

import argparse

from . import scrapers, get_all_scrapers, get_scraper_for_publisher
from .tools import serialize, get_chunks

from amcat4apiclient import AmcatClient

parser = argparse.ArgumentParser()
parser.add_argument("publisher", help="Publisher of the scraper to run")
parser.add_argument("server", help="AmCAT host name",)
parser.add_argument("index", help="AmCAT index")
parser.add_argument("--batchsize", help="Batch size for uploading to AmCAT", type=int, default=100)
parser.add_argument("--url", help="Test single url")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(name)-12s %(levelname)-5s] %(message)s')

scraper_class = get_scraper_for_publisher(args.publisher)
scraper = scraper_class()

if args.url:
    a = scraper.scrape_article(args.url)
    print(json.dumps(a, indent=5, default=serialize))
    sys.exit()

conn = AmcatClient(args.server, "admin", "admin")
if not conn.check_index(args.index):
    conn.create_index(args.index)

logging.info(f"Scraping {scraper} into AmCAT {args.server}:{args.index}")
urls = {a.get('url') for a in conn.query(args.index, filters={"publisher": scraper.PUBLISHER}, fields=["url"])}

logging.info(f"Already {len(urls)} in AmCAT")

articles = scraper.scrape_articles(urls)
for batch in get_chunks(articles, batch_size=args.batchsize):
    print(f"!!! Uploading {len(batch)} articles")
    conn.upload_documents(args.index, batch)

