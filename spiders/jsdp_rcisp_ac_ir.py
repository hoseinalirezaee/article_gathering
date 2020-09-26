import os

from scrapy import Request
from scrapy import Spider
from scrapy.http.response import Response

from utils import HTMLParser


class JSDPSpider(Spider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = HTMLParser()

    custom_settings = {
        'ITEM_PIPELINES': {
            'pipelines.SavePipeline': 1
        }
    }

    name = 'http://jsdp.rcisp.ac.ir'

    start_urls = ['http://jsdp.rcisp.ac.ir/mag-articles.php']

    def parse(self, response: Response, **kwargs):
        articles = response.xpath('//div[@class="pad5 english_article persian_article small_font"]')
        for article in articles:
            download_url = article.css('.article_links').xpath('(.//a)[3]/@href').get()
            download_url = response.urljoin(download_url)

            info_url = article.css('.article_links').xpath('(.//a)[4]/@href').get()
            info_url = response.urljoin(info_url)

            yield Request(info_url, cb_kwargs={'download_url': download_url}, callback=self.parse_info)

    def parse_info(self, response, download_url):
        response.selector.remove_namespaces()

        volume = response.xpath('//volume/text()').get()
        volume = int(volume) if volume else None

        number = response.xpath('//number/text()').get()
        number = int(number) if number else None

        title_fa = response.xpath('//article/title_fa/text()').get()
        if title_fa:
            title_fa = title_fa.strip()

        title_en = response.xpath('//article/title/text()').get()
        if title_en:
            title_en.strip()

        summary_fa = response.xpath('//article/abstract_fa/text()').get()
        if summary_fa:
            self.parser.reset()
            self.parser.feed(summary_fa)
            summary_fa = self.parser.get_text()
            summary_fa = summary_fa.strip()

        summary_en = response.xpath('//article/abstract/text()').get()
        if summary_en:
            self.parser.reset()
            self.parser.feed(summary_en)
            summary_en = self.parser.get_text()
            summary_en = summary_en.strip()

        keywords_fa = response.xpath('//article/keyword_fa//text()').get()
        if keywords_fa:
            keywords_fa = keywords_fa.split(',')
            keywords_fa = list(map(lambda k: k.strip(), keywords_fa))

        keywords_en = response.xpath('//article/keyword//text()').get()
        if keywords_en:
            keywords_en = keywords_en.split(',')
            keywords_en = list(map(lambda k: k.strip(), keywords_en))

        file_name = os.path.basename(download_url)

        yield {
            'volume': volume,
            'number': number,
            'file_name': file_name,
            'title_fa': title_fa,
            'title_en': title_en,
            'summary_fa': summary_fa,
            'summary_en': summary_en,
            'keywords_fa': keywords_fa,
            'keywords_en': keywords_en,
            'download_url': download_url
        }
