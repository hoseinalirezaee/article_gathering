from html import parser
from io import StringIO

from scrapy.settings import Settings

import settings as settings_module


class HTMLParser(parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = StringIO()

    def handle_data(self, data):
        self.text.write(data)

    def get_text(self):
        return self.text.getvalue()

    def reset(self):
        super().reset()
        self.text = StringIO()


def get_settings():
    settings = Settings()
    settings.setmodule(settings_module)
    return settings
