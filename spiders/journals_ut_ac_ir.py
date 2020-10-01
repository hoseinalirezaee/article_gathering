import os
import re

from langdetect import detect
from scrapy import Spider, Request

from utils import HTMLParser

number_pattern = re.compile(r'\d+')


class UTACSpider(Spider):
    name = 'journals_ut_ac_ir'

    custom_settings = {
        'ITEM_PIPELINES': {
            'pipelines.SavePipeline': 1
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = HTMLParser()

    start_urls = ['https://journals.ut.ac.ir/sitemap.xml']

    def parse(self, response, **kwargs):
        response.selector.remove_namespaces()
        links = response.xpath('//loc/text()').re(r'.*article_\d+\.html')

        for link in links:
            yield Request(link.replace('http', 'https'), callback=self.parse_page)

    def parse_page(self, response, **kwargs):
        o = {}

        t = response.xpath('(//span[@id="ar_row_ind"]/following-sibling::a)[1]/text()').get()
        t = re.findall(number_pattern, t)
        try:
            volume = int(t[0])
            number = int(t[1])
        except (IndexError, ValueError):
            volume = None
            number = None

        download_url = response.xpath('//a[@class="pdf"]/@href').get()
        download_url = response.urljoin(download_url)

        if download_url:
            file_name = os.path.basename(download_url)
        else:
            file_name = None

        title = response.xpath('//h1[@class="citation_title"]/text()').get()
        if title:
            self.parser.reset()
            self.parser.feed(title)
            title = self.parser.get_text()
            d_l = detect(title)
            if d_l == 'fa':
                t = {'title_fa': title}
            elif d_l == 'en':
                t = {'title_en': title}
            else:
                t = {}
            o.update(t)

        summary = response.xpath('//td[@id="abs_fa"]').get()
        self.parser.reset()
        self.parser.feed(summary)
        summary = self.parser.get_text()
        if summary:
            d_l = detect(summary)
            if d_l == 'fa':
                t = {'summary_fa': summary}
            elif d_l == 'en':
                t = {'summary_en': summary}
            else:
                t = {}
            o.update(t)

        o.update({
            'volume': volume,
            'number': number,
            'file_name': file_name,
            'download_url': download_url
        })

        keywords = response.xpath('//a[starts-with(@href, "./?_action=article&kw=")]/text()').getall()

        keywords_fa = []
        keywords_en = []

        for kw in keywords:
            d_l = detect(kw)
            if d_l == 'fa':
                keywords_fa.append(kw)
            elif d_l == 'en':
                keywords_en.append(kw)

        if keywords_fa:
            o['keywords_fa'] = keywords_fa

        if keywords_en:
            o['keywords_en'] = keywords_en

        yield o