__all__ = (
    'ComicFuzUrlParser',
)

import re
from urllib.parse import unquote, urlparse

from ..definition import *
from ..util import *


class ComicFuzUrlParser:
    RE_CID = re.compile(r'cid=(.+?)&', re.I)
    RE_CTI = re.compile(r'cti=(.+?)&', re.I)

    @classmethod
    def parse(cls, url: str) -> ComicFuzUrlInfo:
        """
        Parse infomation from given url.

        param url: The reader page on Comic FUZ.
        return: ComicFuzUrlInfo. return None if failed to parse.
        """

        cid_match = cls.RE_CID.search(url)
        ctr_match = cls.RE_CTI.search(url)
        if cid_match is None or ctr_match is None:
            raise RuntimeError("Unable to parse ctr or cid from URL")

        manga_name = unquote(ctr_match[1]).strip()
        cid = unquote(cid_match[1]).strip()
        manga_dir_name = PathUtil.strip_bad_char(manga_name).strip()

        url_parse_result = urlparse(url)

        return ComicFuzUrlInfo(
            raw_url=url,
            url_scheme=url_parse_result.scheme,
            net_loc=url_parse_result.netloc,
            manga_name=manga_name,
            manga_dir_name=manga_dir_name,
            cid=cid,
        )
