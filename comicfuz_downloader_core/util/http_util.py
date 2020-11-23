__all__ = (
    'HttpUtil',
)

from http.cookiejar import MozillaCookieJar
from pathlib import Path
from typing import Any, Mapping, Optional

import chardet
import requests
from requests import Session


class HttpUtil:
    COMMON_HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'Accept-Language': 'ja',
        'Accept': '*/*',
    }

    def __init__(self, cookies_txt_path: Path, proxy: str = ''):
        """
        proxy: Proxies. The syntax is scheme://[user:password@]host:port.
        """
        self.sess = Session()

        # Load cookies
        jar = MozillaCookieJar(cookies_txt_path)
        jar.load(ignore_discard=True, ignore_expires=True)
        self.sess.cookies = jar

        # Set proxy
        if proxy:
            self.set_proxy(proxy)

    def set_proxy(self, proxy: str):
        self.sess.proxies = {
            'http': proxy,
            'https': proxy,
        }

    def get(self, url, headers: Optional[Mapping[str, Any]] = None, /, **kwargs: any) -> requests.Response:
        if headers is None:
            headers = {}

        return self.sess.get(url, headers={
            **self.COMMON_HEADER,
            **headers,
        }, **kwargs)

    @staticmethod
    def read_text(response: requests.Response) -> str:
        res_body_bytes = response.content
        encoding = chardet.detect(res_body_bytes)['encoding']
        text = res_body_bytes.decode(encoding=encoding)

        return text
