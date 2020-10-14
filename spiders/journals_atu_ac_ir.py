from scrapy import Request

from spiders.journals_ut_ac_ir import UTACSpider


class ATUSpider(UTACSpider):
    name = 'atu'

    start_urls = ['http://journals.atu.ac.ir/sitemap.xml']

    def parse(self, response, **kwargs):
        response.selector.remove_namespaces()
        links = response.xpath('//loc/text()').re(r'.*article_\d+\.html')

        for link in links:
            yield Request(link, callback=self.parse_page)
