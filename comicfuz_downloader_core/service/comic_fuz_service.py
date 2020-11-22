__all__ = (
    'ComicFuzService',
)

import json
from typing import Any, Dict, Tuple, Iterable
from urllib.parse import urljoin

import requests

from ..definition import *
from ..util import *

LICENSE_BASE_URL = '{scheme}://{net_loc}/api4js/contents/license?cid={cid}'


class ComicFuzService:

    @staticmethod
    def __join_add_query_str(license: ComicFuzLicense, extra_url: str):
        url = urljoin(license.base_url, extra_url)
        return url + license.policy_query_str

    @classmethod
    def __read_json(cls, resp: requests.Response, ensured_key: Iterable[str] = ()) -> Dict[str, Any]:
        if resp.status_code != 200:
            raise RuntimeError('HTTP status code is not 200.')

        resp_json = json.loads(HttpUtil.read_text(resp))
        for k in ensured_key:
            value = resp_json.get(k)
            if value is None or value == '':
                raise RuntimeError(f'This key cannot be found in server response: {k}')

        return resp_json

    @classmethod
    def get_license_and_cfg_pack(
            cls, url_info: ComicFuzUrlInfo, http_util: HttpUtil,
    ) -> Tuple[ComicFuzLicense, Dict[str, Any]]:
        # >>> get license <<<
        resp = http_util.get(LICENSE_BASE_URL.format(
            scheme=url_info.url_scheme,
            net_loc=url_info.net_loc,
            cid=url_info.cid,
        ), {
            'Referer': url_info.raw_url
        })
        resp_json = cls.__read_json(resp, ('url', 'auth_info'))

        license = ComicFuzLicense(
            base_url=resp_json['url'],
            policy_query_str='?' + '&'.join(f'{x}={y}' for x, y in resp_json['auth_info'].items()),
        )

        # >>> get configuration pack <<<
        cfg_pack_url = cls.__join_add_query_str(license, 'configuration_pack.json')
        resp = http_util.get(cfg_pack_url, {
            'origin': 'https://comic-fuz.com',
            'referer': 'https://comic-fuz.com/',
        })
        cfg_pack = cls.__read_json(resp)

        # return both
        return license, cfg_pack

    @classmethod
    def get_image(cls, image_path: str, license: ComicFuzLicense, http_util: HttpUtil) -> bytes:
        url = cls.__join_add_query_str(license, image_path + '/0.jpeg')
        resp = http_util.get(url, {
            'Referer': 'https://comic-fuz.com'
        })
        if resp.status_code != 200:
            raise RuntimeError('Failed to get image')

        return resp.content
