import re

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from scrapy import Spider, Request
from scrapy import signals
from scrapy.exceptions import DontCloseSpider

pattern = re.compile(r'https://civilica.com/doc/\d+/')


class CivilicaSpider(Spider):
    name = 'civilica'

    start_urls = ['https://civilica.com/sitemap/']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collections = None

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_idle, signals.spider_idle)
        return spider

    def spider_idle(self, spider):
        try:
            collection = next(self.collections)
        except StopIteration:
            pass
        else:
            yield Request(collection, callback=self.parse_collection)
            raise DontCloseSpider()

    def parse(self, response, **kwargs):
        response.selector.remove_namespaces()
        doc_collections: list = response.xpath('//loc/text()').re(r'.*docs/\d+/')
        self.collections = (url for url in doc_collections)

        try:
            url = next(self.collections)
            yield Request(url, callback=self.parse_collection)
        except StopIteration:
            pass

    def parse_collection(self, response, **kwargs):
        docs = re.finditer(pattern, response.text)
        for doc in docs:
            yield Request(doc.group(), method='POST', callback=self.parse_doc)

    def parse_doc(self, response, **kwargs):

        try:
            record = response.json()['record']
        except KeyError:
            return

        title = record['title']

        try:
            if detect(title) != 'fa':
                return
        except LangDetectException:
            return
        summary = record['abstract']

        volume = record['LegalPerson']['volume']
        number = record['LegalPerson']['issue']

        keywords = record['keywords']
        if keywords:
            keywords = re.split(r'[،,-]', keywords)

        keywords_en = record['keywords_en']
        if keywords_en:
            keywords_en = re.split(r'[،,-]', keywords_en)

        yield {
            'title_fa': title,
            'title_en': record['title_en'],
            'summary_fa': summary,
            'summary_en': record['keywords_en'],
            'keywords_fa': keywords,
            'keywords_en': keywords_en,
            'volume': volume,
            'number': number,
            'file_name': None,
            'download_url': None
        }
