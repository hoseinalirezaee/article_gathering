import re
from urllib.parse import urljoin

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from scrapy import Spider, Request

from utils import HTMLParser

pattern = re.compile(r'\d+')


class SBUSpider(Spider):
    name = 'sbu_ac_ir'

    start_urls = ['http://scj.sbu.ac.ir/index.php/index/index/journalsLoadedByAjax?category=all']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = HTMLParser()

    def parse(self, response, **kwargs):
        journals = response.json()
        for j in journals:
            path = j['path']
            archive_path = urljoin(path, '/issue/archive')
            yield Request(archive_path, callback=self.parse_journal)

    def parse_journal(self, response, **kwargs):
        next_page = response.xpath('//ul[@class="pagination"]/li[last()-1][@class="waves-effect"]/a/@href').get()
        if next_page:
            yield Request(next_page, callback=self.parse_journal)

        issues = response.xpath('//a/@href').re(r'.*/view/\d+')
        for issue in issues:
            yield Request(urljoin(issue + '/', 'showToc'), callback=self.parse_issue)

    def parse_issue(self, response, **kwargs):
        temp = response.css('.MDbreadcrumb').xpath('li[last()]//a/text()').get()
        if temp:
            temp = re.findall(pattern, temp)[:2]
            if len(temp) == 2:
                volume, number = temp
            else:
                volume, number = None, None
        else:
            volume, number = None, None

        articles = response.css('.tocArticle')
        for article_node in articles:
            title = article_node.xpath('.//div[@class="tocTitle"]/a/text()').get()
            try:
                if title and detect(title) != 'fa':
                    continue
            except LangDetectException:
                continue

            download_link = article_node.xpath('.//div[@class="tocGalleys"]/a/@href').get()
            download_link = download_link.replace('view', 'download') if download_link else None

            if download_link:
                temp = re.findall(pattern, download_link)
                file_name = '_'.join(temp)
                file_name = 'sbu_%s.pdf' % file_name
            else:
                download_link = None
                file_name = None

            temp = article_node.css('.secondary-content').xpath('@href').get()
            if not temp:
                continue
            temp = response.xpath('//div[@id="%s"]' % temp[1:])
            if not temp:
                continue
            temp = temp.xpath('.//div[@class="modal-content"]/*').getall()
            summary_fa = ''
            keywords_fa = ''
            phase = 1
            for element in temp:
                self.parser.reset()
                self.parser.feed(element)
                data = self.parser.get_text()

                if data == 'چکیده':
                    continue
                if data == 'واژگان کلیدی':
                    phase = 2
                    continue
                try:
                    label = detect(data)
                except LangDetectException:
                    continue
                if label == 'fa' and phase == 1:
                    summary_fa += data
                    continue
                if label == 'fa' and phase == 2:
                    keywords_fa += data
            if keywords_fa:

                keywords_fa = list(map(lambda x: x.strip(), re.split(r'[؛،,-]', keywords_fa)))
            else:
                keywords_fa = None

            if not summary_fa:
                summary_fa = None

            yield {
                'volume': volume,
                'number': number,
                'file_name': '%s_%s' % (self.name, file_name) if file_name else None,
                'title_fa': title.strip() if title else None,
                'title_en': None,
                'summary_fa': summary_fa.strip() if summary_fa else None,
                'summary_en': None,
                'keywords_fa': keywords_fa,
                'keywords_en': None,
                'download_url': download_link
            }
