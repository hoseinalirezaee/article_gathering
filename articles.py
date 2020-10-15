import json
import os

import click
from scrapy import crawler
from scrapy import signals as scrapy_signals

import signals
from spiders.civilica_com import CivilicaSpider
from spiders.download import DownloadSpider
from spiders.journals_atu_ac_ir import ATUSpider
from spiders.journals_ut_ac_ir import UTACSpider
from spiders.jsdp_rcisp_ac_ir import JSDPSpider
from spiders.scj_sbu_ac_ir import SBUSpider
from utils import get_settings

spider_classes = [
    UTACSpider,
    JSDPSpider,
    SBUSpider,
    ATUSpider,
    CivilicaSpider
]

@click.group('article')
def article():
    pass


def item_scraped(item, spider, **kwargs):
    try:
        print('finished: %s (%s) (%s)' % (item['title_fa'], item['file_name'], spider.name))
    except KeyError:
        pass


@article.command('update', help='Updates articles list.')
def update():
    print('Updating articles info. Please wait...')
    save_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)
    save_path = os.path.join(save_dir, 'info.jsonlines')
    settings = get_settings()
    settings.set('FEEDS',
                 {save_path: {'format': 'jsonlines', 'overwrite': True, 'item_export_kwargs': {'sort_keys': True}}})
    cp = crawler.CrawlerProcess(settings)

    for spider_cls in spider_classes:
        c = crawler.Crawler(spider_cls, settings)
        c.signals.connect(item_scraped, scrapy_signals.item_scraped)
        cp.crawl(c)

    cp.start()
    print('Updating finished.')


def downloaded(file_name, total_count, downloaded_count, is_pdf):
    if is_pdf:
        print('%d of %d downloaded. (%s)' % (downloaded_count, total_count, file_name))
    else:
        print('%d of %d downloaded. DROPPED (%s is not pdf.)' % (downloaded_count, total_count, file_name))


@article.command('download', help='Downloads one or more articles.')
def download():
    info_path = os.path.join(os.getcwd(), 'data/info.jsonlines')
    if not os.path.isfile(info_path):
        print('Use `update` command first.')
        return

    save_dir = os.path.join(os.getcwd(), 'data/files/')
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)

    download_urls = []
    with open(info_path, 'rt') as file:
        for line in file:
            article_info = json.loads(line)
            file_name = article_info['file_name']
            download_url = article_info['download_url']
            if not file_name or not download_url or os.path.isfile(os.path.join(save_dir, file_name)):
                continue
            download_urls.append({'url': article_info['download_url'], 'file_name': file_name})
    print('Total files: %d' % len(download_urls))
    cp = crawler.CrawlerProcess(get_settings())
    cr = crawler.Crawler(DownloadSpider, get_settings())
    cr.signals.connect(downloaded, signal=signals.file_downloaded)
    cp.crawl(cr, save_dir=save_dir, download_list=download_urls)
    cp.start()


if __name__ == '__main__':
    article()
