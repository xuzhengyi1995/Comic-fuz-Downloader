__all__ = (
    'CfgPackParser',
)

from typing import Dict, Any, List

from ..definition import *
from ..util import *


class CfgPackParser:
    @classmethod
    def parse(cls, config_pack: Dict[str, Any]) -> List[ComicFuzFileItem]:
        contents = config_pack.get('configuration', {}).get('contents')
        if contents is None:
            raise RuntimeError('Key `contents` not found in configuration_packs.json')
        max_length = len(str(len(contents)))

        result: List[ComicFuzFileItem] = []
        for i, file in enumerate(contents):
            file_path = file['file']
            page_info = config_pack[file_path]['FileLinkInfo']['PageLinkInfoList'][0]['Page']
            page_no = page_info['No']
            dummy_pixels = (page_info['DummyWidth'], page_info['DummyHeight'])
            file_disk_name_index = str(i).zfill(max_length)

            result.append(ComicFuzFileItem(
                index=i, file_path=file_path,
                file_disk_name=file_disk_name_index + '_' + PathUtil.strip_bad_char(file_path),
                page_no=page_no, dummy_pixels=dummy_pixels,
            ))

        return result
