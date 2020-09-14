BOT_NAME = 'articles'

SPIDER_MODULES = ['spiders']

NEWSPIDER_MODULE = 'articles.spiders'

USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; vivo 1713 Build/MRA58K)'

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 0.2
CONCURRENT_REQUESTS = 5
CONCURRENT_REQUESTS_PER_DOMAIN = 5

RETRY_ENABLED = True
RETRY_HTTP_CODES = [403]
RETRY_TIMES = 5

DOWNLOADER_MIDDLEWARES = {
    # Engine side
    'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': 100,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': None,
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
    'scrapy.downloadermiddlewares.stats.DownloaderStats': None,
    'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': None,
    # Downloader side
}

EXTENSIONS = {
    'scrapy.extensions.corestats.CoreStats': 0,
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy.extensions.memusage.MemoryUsage': None,
    'scrapy.extensions.memdebug.MemoryDebugger': None,
    'scrapy.extensions.closespider.CloseSpider': None,
    'scrapy.extensions.feedexport.FeedExporter': None,
    'scrapy.extensions.logstats.LogStats': None,
    'scrapy.extensions.spiderstate.SpiderState': None,
    'scrapy.extensions.throttle.AutoThrottle': None,
}

SPIDER_MIDDLEWARES = {
    # Engine side
    'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 50,
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 500,
    'scrapy.spidermiddlewares.referer.RefererMiddleware': 700,
    'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': 800,
    'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
    # Spider side
}

LOG_LEVEL = 'ERROR'
