__all__ = (
    'ThreadDownloadImage',
)
from threading import Thread
from ..util import *

class ThreadDownloadImage(Thread):
    def __init__(self, http_util: HttpUtil):
        super().__init__()
        self.hutil = http_util

    def run(self):
        pass
