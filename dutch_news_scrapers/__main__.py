import argparse
import datetime
import json
import logging
from collections import Counter
from typing import Iterable

from amcat4apiclient import AmcatClient
from requests import HTTPError

from dutch_news_scrapers.scraper import Scraper
from dutch_news_scrapers.scrapers import get_all_scrapers, get_scraper_for_publisher, get_scraper_for_url
from dutch_news_scrapers.tools import get_chunks


def texts_status(args):
    conn = AmcatClient(args.server, "admin", "admin")
    counts = {}

    for d in conn.query(args.index, fields=["publisher", "url", "status"]):
        publisher = d['publisher']
        if publisher not in counts:
            counts[publisher] = {"complete": 0, "incomplete": 0, "missing": 0, "skip": 0}
        c = counts[publisher]
        if 'url' not in d:
            c['skip'] += 1
        elif d['status'] == "incomplete":
            try:
                scraper = get_scraper_for_url(d['url'])
                c['incomplete'] += 1
            except ValueError:
                c['missing'] += 1
        else:
            c['complete'] += 1
    print(f"{'Publisher':30} {'Complete':>10} {'Incomplete':>10} {'Missing':>10} {'Skip':>10}")
    for publisher, c in counts.items():
        print(f"{publisher:30} {c['complete']:10} {c['incomplete']:10} {c['missing']:10} {c['skip']:10}")


def update_texts(args):
    scraper_class = get_scraper_for_publisher(args.publisher)
    scraper = scraper_class()
    conn = AmcatClient(args.server)

    try:
        conn.create_index(args.index)
    except HTTPError as e:
        # Probably, index already exists
        return


    articles = conn.query(args.index, fields=["url"], filters={'publisher': args.publisher, 'status': 'incomplete'})
    n = 0
    for d in articles:
        url = d.get('url')
        print(f"  {d['_id']}: {url}")
        if not url:
            continue
        try:
            text = scraper.scrape_text(url)
        except HTTPError as e:
            if e.response.status_code in (403, 404):
                logging.warning(f"HTTP {e.response.status_code} on {url}, setting status to error and skipping")
                conn.update_document(args.index, d['_id'], {'status': 'error'})
                continue
            else:
                raise
        n += 1
        conn.update_document(args.index, d['_id'], {'text': text, 'status': 'complete'})
    print(f"Updated {n} documents")


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
   # assert isinstance(scraper, Scraper)

    conn = AmcatClient(args.server)
    if args.delete_index:
        conn.delete_index(args.index)
    if not conn.check_index(args.index):
        conn.create_index(args.index)
    conn.set_fields(args.index, scraper.columns())

    logging.info(f"Scraping {scraper} into AmCAT {args.server}:{args.index}")
    urls = {a.get('url') for a in conn.query(args.index, filters={"publisher": scraper.PUBLISHER}, fields=["url"])}

    logging.info(f"Already {len(urls)} in AmCAT")

    def filter_by_from_date(articles: Iterable[dict], from_date: datetime.date):
        for a in articles:
            if date(a['date']) < from_date:
                break
            yield a

    def filter_by_to_date(articles: Iterable[dict], to_date: datetime.date):
        for a in articles:
            if date(a['date']) <= to_date:
                yield a

    articles = scraper.scrape_articles(urls)
    if args.from_date:
        articles = filter_by_from_date(articles, from_date=args.from_date)
    if args.to_date:
        articles = filter_by_to_date(articles, to_date=args.from_date)

    for batch in get_chunks(articles, batch_size=args.batchsize):
        print(f"!!! Uploading {len(batch)} articles")
        if not args.dry_run:
            conn.upload_documents(args.index, batch)
        else:
            for article in batch:
                print(json.dumps(article, indent=2))


def scrapeurl(args):
    scraper_class = get_scraper_for_url(args.url)
    if issubclass(scraper_class, Scraper):
        a = scraper_class().scrape_article(args.url)
        print(json.dumps(a, indent=4))
    else:
        a = scraper_class().scrape_text(args.url)
        print(a)


def date(s):
    try:
        if "T" in s:
            return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
        else:
            return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="action", title="action", help='Action to perform:', required=True)

p = subparsers.add_parser('list', help='List scrapers')
p.set_defaults(func=listscrapers)

p = subparsers.add_parser('run', help='Run a scraper for a single publisher')
p.add_argument("server", help="AmCAT host name",)
p.add_argument("index", help="AmCAT index")
p.add_argument("publisher", help="Publisher of the scraper to run")
p.add_argument("--batchsize", help="Batch size for uploading to AmCAT", type=int, default=100)
p.add_argument("--from_date", type=date)
p.add_argument("--to_date", type=date)
p.add_argument("--dry-run", action="store_true")
p.add_argument("--delete-index", action="store_true", help="Delete (and recreate) index before scraping")
p.set_defaults(func=run)

p = subparsers.add_parser('texts-update', help='Add texts to existing documents')
p.add_argument("server", help="AmCAT host name",)
p.add_argument("index", help="AmCAT index")
p.add_argument("publisher", help="Publisher of the scraper to run")
p.set_defaults(func=update_texts)

p = subparsers.add_parser('texts-status', help='View text and scraper status')
p.add_argument("server", help="AmCAT host name",)
p.add_argument("index", help="AmCAT index")
p.set_defaults(func=texts_status)

p = subparsers.add_parser('scrape-url', help='Run a scraper for a single article')
p.add_argument("url", help="URL of the article to scrape")
p.add_argument("--dry-run", help="Dry run: print result but don't upload", action="store_true")
p.set_defaults(func=scrapeurl)

args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(name)-12s %(levelname)-5s] %(message)s')
args.func(args)
