import re
from lxml.html import Element
from lxml import html
from dutch_news_scrapers.scraper import Scraper

def create_cookie(domain, name, value):
    return {
        "name": name,
        "value": value,
        "domain": domain,
    }


class TELScraper(Scraper):
    DOMAIN = "telegraaf.nl"
    COOKIES = {
        '__cfduid':'d56655838cd13e536c63a84867a1cd55c1585123110',
        'clientid':"ck871dfn22m9y568461ch66fv",
        'didomi_token':'eyJ1c2VyX2lkIjoiMTcxMTBiMzMtMTBjYS02YTViLWFkNDAtMmQwMGFjNGJlZTY2IiwiY3JlYXRlZCI6IjIwMjAtMDMtMjVUMDc6NTg6MzEuMjA4WiIsInVwZGF0ZWQiOiIyMDIwLTAzLTI1VDA3OjU4OjUwLjk0OFoiLCJ2ZW5kb3JzIjp7ImVuYWJsZWQiOlsiZ29vZ2xlIiwiZmFjZWJvb2siLCJjOm5sLXByb2ZpZWwiXSwiZGlzYWJsZWQiOltdfSwicHVycG9zZXMiOnsiZW5hYmxlZCI6WyJmdW5jdGlvbmVlbCIsInNvY2lhbF9tZWRpYSIsIm5sX3Byb2ZpZWwiLCJjb29raWVzIiwiYWR2ZXJ0aXNpbmdfcGVyc29uYWxpemF0aW9uIiwiY29udGVudF9wZXJzb25hbGl6YXRpb24iLCJhZF9kZWxpdmVyeSIsImFuYWx5dGljcyJdLCJkaXNhYmxlZCI6W119fQ==',
        'euconsent': 'BOwzpeIOwzphNAHABBNLC--AAAAuhr_7__7-_9_-_f__9uj3Or_v_f__32ccL59v_h_7v-_7fi_20nV4u_1vft9yfk1-5ctDztp507iakivXmqdeb9v_nz3_5pxP78k89r7337Ew_v8_v-b7BCON_YxEiA',
        'OB-USER-TOKEN': '82e48dea-c07a-420c-a5e2-cece4269fb48',
        'paywallversion': '1',
    }

    def initialize(self):
        for name, value in self.COOKIES.items():
            self.session.cookies.set(**create_cookie("www.telegraaf.nl", name, value))
            r = self.session.get("https://www.telegraaf.nl/nieuws/1071777683/pvd-a-ers-houden-samengaan-met-groen-links-af")
            r.raise_for_status()

    def scrape_text(self, url):
        page = self.session.get(url)
        page.raise_for_status()
        open("/tmp/test7.html", "w").write(page.text)
        tree = html.fromstring(page.text)
        for label in tree.cssselect("span.label"):
            if label.text_content().strip().startswith("Liveblog"):
                return None
        lead_ps = tree.cssselect('p.ArticleIntroBlock__paragraph')
        body_ps = tree.xpath('//div[@data-element="articleBodyBlocks"]/p')
        text = "\n\n".join(p.text_content() for p in lead_ps + body_ps)
        return text


class VKScraper(Scraper):
    DOMAIN = "volkskrant.nl"
    COOKIE_URL = "https://www.volkskrant.nl/privacy-wall/accept?redirectUri=%2f&pwv=2&pws=functional%7Canalytics%7Ccontent_recommendation%7Ctargeted_advertising%7Csocial_media&days=390&referrer="

    def initialize(self):
        r = self.session.post(self.COOKIE_URL)
        r.raise_for_status()

    def scrape_text(self, url):
        page = self.session.get(url)
        if page.status_code == 404:
            return
        page.raise_for_status()
        open("/tmp/test7.html", "w").write(page.text)
        tree = html.fromstring(page.text)
        lead = tree.cssselect("p.artstyle__intro")
        if not lead:
            lead ="-"
        lead_ps = tree.cssselect('p.p.artstyle__text')
        body_ps = tree.cssselect('p.artstyle__text')
        text = "\n\n".join(p.text_content() for p in lead_ps + body_ps)
        text = re.sub("\n\n\s*", "\n\n", text)
        return text

class TRWScraper(Scraper):
    DOMAIN = "trouw.nl"
    COOKIE_URL = "https://www.trouw.nl/privacy-wall/accept?redirectUri=%2f&pwv=2&pws=functional%7Canalytics%7Ccontent_recommendation%7Ctargeted_advertising%7Csocial_media&days=390&referrer="

    def initialize(self):
        r = self.session.post(self.COOKIE_URL)
        r.raise_for_status()

    def scrape_text(self, url):
        print(f"TRWScraper: {url}")
        page = self.session.get(url)
        if page.status_code == 404:
            return
        page.raise_for_status()
        open("/tmp/test7.html", "w").write(page.text)
        tree = html.fromstring(page.text)
        lead = tree.cssselect("p.artstyle__intro")
        if not lead:
            lead ="-"
        lead_ps = tree.cssselect('p.p.artstyle__text')
        body_ps = tree.cssselect('p.artstyle__text')
        text = "\n\n".join(p.text_content() for p in lead_ps + body_ps)
        text = re.sub("\n\n\s*", "\n\n", text)
        return text


class ADScraper(Scraper):
    DOMAIN = "ad.nl"
    COOKIE_URL = "https://www.ad.nl/privacy-gate/accept?redirectUri=%2f&pwv=2&pws=functional%7Canalytics%7Ccontent_recommendation%7Ctargeted_advertising%7Csocial_media&days=390&referrer="

    def initialize(self):
        r = self.session.post(self.COOKIE_URL)
        r.raise_for_status()

    def scrape_text(self, url):
        page = self.session.get(url)
        if page.status_code == 404:
            return
        page.raise_for_status()
        open("/tmp/test7.html", "w").write(page.text)
        tree = html.fromstring(page.text)
        lead_ps = tree.cssselect('p.article__intro')
        body_ps = tree.cssselect('p.article__paragraph')
        text = "\n\n".join(p.text_content() for p in lead_ps + body_ps)
        text = re.sub("\n\n\s*", "\n\n", text)
        return text


class NUScraper(Scraper):
    DOMAIN = "nu.nl"

    def parse_html(self, page) -> str:
        for label in page.cssselect("span.label"):
            if label.text_content().strip().startswith("Liveblog"):
                return None
        text = page.cssselect('div.block-wrapper div.block-content > p')
        if not text:
            text = page.cssselect('div.caption-wrapper')
            if not text:
                text = page.cssselect('div.block-content')
        text = "\n\n".join(p.text_content() for p in text)
        text = re.sub("\n\n\s*", "\n\n", text)
        return text


class NOSScraper(Scraper):
    DOMAIN = "nos.nl"

    def parse_html(self, page: Element) -> str:
        text = page.cssselect("p.text_3v_J6Y0G")
        if not text:
            text = page.cssselect("header.liveblog-header")
            if not text:
                text = page.cssselect("div.article_textwrap")
        text = "\n\n".join(p.text_content() for p in text)
        text = re.sub("\n\n\s*", "\n\n", text)
        return text

class NRCScraper(Scraper):
    DOMAIN = "nrc.nl"

    def parse_html(self, page) -> str:
        lead_ps = page.cssselect('div.intro.article__intro')
        body_ps = page.cssselect('div.content.article__content > p')
        text = "\n\n".join(p.text_content() for p in lead_ps + body_ps)
        text = re.sub("\n\n\s*", "\n\n", text)
        return text

class RTLScraper(Scraper):
    DOMAIN = "rtlnieuws.nl"

    def parse_html(self, page) -> str:
        lead_ps = page.cssselect('p.lede')
        body_ps = page.cssselect('div.paragraph.paragraph--type--paragraph-text')
        text = "\n\n".join(p.text_content() for p in lead_ps + body_ps)
        text = re.sub("\n\n\s*", "\n\n", text)
        return text
    
    

class OmroepFlevolandScraper(Scraper):
    DOMAIN = "omroepflevoland.nl"
    
    def parse_html(self, page: Element) -> str:
        text = page.cssselect("section.article__content > p")
        text = "\n\n".join(p.text_content() for p in text)
        text = re.sub("\n\n\s*", "\n\n", text)
        return text

class NHNieuwsScraper(Scraper):
    DOMAIN = "nhnieuws.nl"

    def parse_html(self, page: Element) -> str:

        lead = page.cssselect("div.container--detail.intro__text")
        lead = lead[0].text_content()
        text1 = page.cssselect("div.container--detail.detail-text > p")
        text2 = "\n\n".join(p.text_content() for p in text1)
        text = f"{lead}\n\n{text2}"
        text = re.sub("\n\n\s*", "\n\n", text)
        return text

class OmroepGelderlandScraper(Scraper):
    DOMAIN = "omroepgelderland.nl"

    def parse_html(self, page: Element) -> str:

        lead = page.cssselect("div.intro")
        lead = lead[0].text_content()
        text1 = page.cssselect("div.customhtml.newsitem-customhtml.position-relative > p")
        text2 = "\n\n".join(p.text_content() for p in text1)
        text = f"{lead}\n\n{text2}"
        text = re.sub("\n\n\s*", "\n\n", text)
        return text


class OmroepZeelandScraper(Scraper):
    DOMAIN = "omroepzeeland.nl"

    def parse_html(self, page: Element) -> str:
        lead = page.cssselect("div.intro")
        lead = lead[0].text_content()
        text1 = page.cssselect("div.customhtml.newsitem-customhtml.position-relative p")
        text2 = "\n\n".join(p.text_content() for p in text1)
        text = f"{lead}\n\n{text2}"
        text = re.sub("\n\n\s*", "\n\n", text)
        return text


class OmroepRijnmondScraper(Scraper):
    DOMAIN = "rijnmond.nl"

    def parse_html(self, page: Element) -> str:
        lead = page.cssselect("article.article-content div.intro")
        lead = lead[0].text_content()
        text1 = page.cssselect("div.customhtml.newsitem-customhtml.position-relative p")
        text2 = "\n\n".join(p.text_content() for p in text1)
        text = f"{lead}\n\n{text2}"
        text = re.sub("\n\n\s*", "\n\n", text)
        return text

class RTVUtrechtScraper(Scraper):
    DOMAIN = "rtvutrecht.nl"

    def parse_html(self, page: Element) -> str:
        text = page.cssselect("section.page-content > article")
        text = text[0].text_content() 
        return text

class RTVOostScraper(Scraper):
    DOMAIN = "rtvoost.nl"

    def parse_html(self, page: Element) -> str:
        lead = page.cssselect("div.intro")
        lead = lead[0].text_content()
        text1 = page.cssselect("div.customhtml.newsitem-customhtml.position-relative > p")
        text2 = "\n\n".join(p.text_content() for p in text1)
        text = f"{lead}\n\n{text2}"
        text = re.sub("\n\n\s*", "\n\n", text)
        return text



class LimburgScraper(Scraper):
    DOMAIN = "1limburg.nl"

    def parse_html(self, page: Element) -> str:
        lead = page.cssselect("div.article-lead")
        lead = lead[0].text_content()
        text1 = page.cssselect("div.article-body > p")
        text2 = "\n\n".join(p.text_content() for p in text1)
        text = f"{lead}\n\n{text2}"
        text = re.sub("\n\n\s*", "\n\n", text)
        return text


class AT5Scraper(Scraper):
    DOMAIN = "AT5.nl"

    def parse_html(self, page: Element) -> str:
        lead = page.cssselect("div.container--detail.intro__text")
        lead = lead[0].text_content()
        text1 = page.cssselect("div.container--detail.detail-text > p")
        text2 = "\n\n".join(p.text_content() for p in text1)
        text = f"{lead}\n\n{text2}"
        text = re.sub("\n\n\s*", "\n\n", text)
        return text


class OmroepWestScraper(Scraper):
    DOMAIN = "omroepwest.nl"

    def parse_html(self, page: Element) -> str:
        lead = page.cssselect("div.intro")
        lead = lead[0].text_content()
        text1 = page.cssselect("div.customhtml.newsitem-customhtml.position-relative > p")
        text2 = "\n\n".join(p.text_content() for p in text1)
        text = f"{lead}\n\n{text2}"
        text = re.sub("\n\n\s*", "\n\n", text)
        return text


class RTVDrentheScraper(Scraper):
    DOMAIN = "rtvdrenthe.nl"

    def parse_html(self, page: Element) -> str:
        lead = page.cssselect("div.intro")
        lead = lead[0].text_content()
        text1 = page.cssselect("div.customhtml.newsitem-customhtml.position-relative > p")
        text2 = "\n\n".join(p.text_content() for p in text1)
        text = f"{lead}\n\n{text2}"
        text = re.sub("\n\n\s*", "\n\n", text)
        return text


class OmroepFryslanScraper(Scraper):
    DOMAIN = "omropfryslan.nl"

    def parse_html(self, page: Element) -> str:
        text1 = page.cssselect("div.article_textwrap > p")
        text = "\n\n".join(p.text_content() for p in text1)
        text = re.sub("\n\n\s*", "\n\n", text)
        return text


class OmroepBrabantScraper(Scraper):
    DOMAIN = "omroepbrabant.nl"

    def parse_html(self, page: Element) -> str:
        text1 = page.cssselect("div.cap-width-Tq > div.content-2v")
        text = "\n\n".join(p.text_content() for p in text1)
        text = re.sub("\n\n\s*", "\n\n", text)
        return text