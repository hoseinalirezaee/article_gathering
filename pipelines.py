import os

import signals


class SaveFilePipeline:
    save_dir = None

    def open_spider(self, spider):
        save_dir = getattr(spider, 'save_dir', os.path.join(os.getcwd(), 'data/files/'))
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)
        self.save_dir = save_dir

    def process_item(self, item, spider):
        file = item.pop('file')
        file_name = item['file_name']
        is_pdf = False
        if file.startswith(b'%PDF'):
            is_pdf = True
            with open(os.path.join(self.save_dir, file_name), 'wb') as f:
                f.write(file)

        spider.crawler.signals.send_catch_log(signal=signals.file_downloaded,
                                              file_name=file_name,
                                              total_count=spider.articles_count,
                                              downloaded_count=spider.downloaded_count,
                                              is_pdf=is_pdf)
        return item
