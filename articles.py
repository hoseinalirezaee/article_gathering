import json
import os

import click
from scrapy import crawler

import signals
from spiders.download_jsdp_rcisp_ac_ir import DownloadSpider
from spiders.jsdp_rcisp_ac_ir import JSDPSpider
from utils import get_settings


@click.group('article')
def article():
    pass


@article.command('update', help='Updates articles list.')
def update():
    print('Updating articles info. Please wait...')
    save_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)
    save_path = os.path.join(save_dir, 'info.json')
    settings = get_settings()
    cp = crawler.CrawlerProcess(settings)
    cp.crawl(JSDPSpider, save_path=save_path)
    cp.start()
    print('Updating finished.')


def downloaded(file_name, total_count, downloaded_count):
    print('%d of %d downloaded. (%s)' % (downloaded_count, total_count, file_name))


@article.command('download', help='Downloads one or more articles.')
def download():
    info_path = os.path.join(os.getcwd(), 'data/info.json')
    if not os.path.isfile(info_path):
        print('Use `update` command first.')
        return

    save_dir = os.path.join(os.getcwd(), 'data/files/')
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)

    download_urls = []
    with open(info_path) as file:
        for line in file:
            article_info = json.loads(line)
            file_name = article_info['file_name']
            if os.path.isfile(os.path.join(save_dir, file_name)):
                continue
            download_urls.append(article_info['download_url'])
    print('Total files: %d' % len(download_urls))
    cp = crawler.CrawlerProcess(get_settings())
    cr = crawler.Crawler(DownloadSpider, get_settings())
    cr.signals.connect(downloaded, signal=signals.file_downloaded)
    cp.crawl(cr, save_dir=save_dir, download_list=download_urls)
    cp.start()


if __name__ == '__main__':
    article()
