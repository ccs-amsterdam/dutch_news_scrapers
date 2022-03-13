import logging
import re

from lxml import html
from lxml.html import HtmlElement


def serialize(obj):
    """JSON serializer that accepts datetime & date"""
    from datetime import datetime, date, time
    if isinstance(obj, date) and not isinstance(obj, datetime):
        obj = datetime.combine(obj, time.min)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, set):
        return sorted(obj)


def get_chunks(sequence, batch_size):
    # TODO can be made more efficient by not creating a new list every time
    buffer = []
    for a in sequence:
        buffer.append(a)
        if len(buffer) >= batch_size:
            yield buffer
            buffer = []
    if buffer:
        yield buffer


def encoding_from_html(tree: HtmlElement):
    for m in tree.cssselect("meta"):
        content = m.get('content')
        if m.get("http-equiv") == "Content-Type" and 'charset' in content:
            if match := re.search("charset=([^;]+)", content):
                return match.group(1)


def response_to_dom(response):
    response.raise_for_status()
    dom = html.fromstring(response.text)
    enc = encoding_from_html(dom)
    if enc and response.encoding != enc:
        logging.warning(f"Switching encoding to {enc}")
        response.encoding = enc
        dom = html.fromstring(response.text)
    return dom
