import os

from scrapy import Request
from scrapy import Spider


class DownloadSpider(Spider):
    name = 'download'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.articles_count = len(getattr(self, 'download_list', []))
        self.downloaded_count = 0

    custom_settings = {
        'ITEM_PIPELINES': {
            'pipelines.SaveFilePipeline': 1
        }
    }

    def start_requests(self):
        download_list = getattr(self, 'download_list', [])
        for item in download_list:
            yield Request(item['url'], cb_kwargs={'file_name': item['file_name']})

    def parse(self, response, **kwargs):
        url = response.url
        file_name = kwargs.get('file_name') or os.path.basename(url)
        self.downloaded_count += 1
        yield {
            'file_name': file_name,
            'file': response.body
        }
