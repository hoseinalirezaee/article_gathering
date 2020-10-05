import os
import re

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
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
        try:
            o = {}

            title = response.xpath('//h1[@class="citation_title"]/text()').get()
            if title:
                self.parser.reset()
                self.parser.feed(title)
                title = self.parser.get_text()
                d_l = detect(title)
                if d_l == 'fa':
                    t = {'title_fa': title}
                else:
                    return None
                t['title_en'] = None
                o.update(t)
            else:
                return None

            t = response.xpath('(//span[@id="ar_row_ind"]/following-sibling::a)[1]/text()').get()
            if t is not None:
                t = re.findall(number_pattern, t)
            try:
                volume = int(t[0])
                number = int(t[1])
            except (IndexError, ValueError, TypeError):
                volume = None
                number = None

            download_url = response.xpath('//a[@class="pdf"]/@href').get()
            download_url = response.urljoin(download_url)

            if download_url:
                file_name = os.path.basename(download_url)
            else:
                file_name = None

            summary = response.xpath('//td[@id="abs_fa"]').get()
            if summary:
                self.parser.reset()
                self.parser.feed(summary)
                summary = self.parser.get_text()
            t = {
                'summary_fa': None,
                'summary_en': None
            }
            if summary:
                d_l = detect(summary)
                if d_l == 'fa':
                    t.update({'summary_fa': summary})
                elif d_l == 'en':
                    t.update({'summary_en': summary})
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

            o['keywords_fa'] = keywords_fa if keywords_fa else None
            o['keywords_en'] = keywords_en if keywords_en else None

            yield o
        except LangDetectException:
            pass
