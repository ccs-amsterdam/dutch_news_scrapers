import argparse
import json
import logging

from amcat4apiclient import AmcatClient

from dutch_news_scrapers.scraper import Scraper
from dutch_news_scrapers.scrapers import get_all_scrapers, get_scraper_for_publisher, get_scraper_for_url
from dutch_news_scrapers.tools import get_chunks


def listscrapers(args):
    print(f"{'Publisher':20} {'Domain':20} {'Type':12} {'Class name':20}")
    for scraper in get_all_scrapers():
        domain = scraper.DOMAIN or "-"
        publisher = scraper.PUBLISHER or "-"
        stype = "Scraper" if issubclass(scraper, Scraper) else "TextScraper"
        print(f"{publisher:20} {domain:20} {stype:12} {scraper.__name__:20}")


def run(args):
    scraper_class = get_scraper_for_publisher(args.publisher)
    scraper = scraper_class()

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


def scrapeurl(args):
    scraper_class = get_scraper_for_url(args.url)
    a = scraper_class().scrape_text(args.url)
    print(a)


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="action", title="action", help='Action to perform:', required=True)

p = subparsers.add_parser('list', help='List scrapers')
p.set_defaults(func=listscrapers)

p = subparsers.add_parser('run', help='Run a scraper for a single publisher')
p.add_argument("server", help="AmCAT host name",)
p.add_argument("index", help="AmCAT index")
p.add_argument("publisher", help="Publisher of the scraper to run")
p.add_argument("--batchsize", help="Batch size for uploading to AmCAT", type=int, default=100)
p.set_defaults(func=run)

p = subparsers.add_parser('scrape-url', help='Run a scraper for a single article')
p.add_argument("url", help="URL of the article to scrape")
p.add_argument("--dry-run", help="Dry run: print result but don't upload", action="store_true")
p.set_defaults(func=scrapeurl)

args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(name)-12s %(levelname)-5s] %(message)s')
args.func(args)
