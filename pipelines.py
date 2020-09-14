import json
import os

import signals


class SavePipeline:
    save_path = None
    file = None

    def open_spider(self, spider):
        self.save_path = getattr(spider, 'save_path', os.getcwd())
        if os.path.isdir(self.save_path):
            self.save_path = os.path.join(self.save_path, 'articles.json')
        self.file = open(self.save_path, 'wt')

    def process_item(self, item, spider):
        self.file.write('%s\n' % json.dumps(item, ensure_ascii=False))
        return item

    def close_spider(self, spider):
        self.file.close()


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
        with open(os.path.join(self.save_dir, file_name), 'wb') as f:
            f.write(file)
        spider.crawler.signals.send_catch_log(signal=signals.file_downloaded,
                                              file_name=file_name,
                                              total_count=spider.articles_count,
                                              downloaded_count=spider.downloaded_count)
        return item
