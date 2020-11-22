__all__ = (
    'ImageDescrambler',
)

from io import BytesIO
from typing import Tuple

import PIL.Image

from ..util import ScrambleCalculator


class ImageDescrambler:
    @classmethod
    def descramble_image(
            cls, org_img_bytes: bytes, pattern: int, dummy_pixels: Tuple[int, int]
    ) -> bytes:
        """
        dummy_pixels: (DummyWidth, DummyHeight)
        """

        orig_img_file = BytesIO(org_img_bytes)
        orig_img = PIL.Image.open(orig_img_file)
        width, height = orig_img.width, orig_img.height

        scramble_data = ScrambleCalculator.get_scramble_data(width, height, pattern)
        dest_img = PIL.Image.new('RGB', (width, height))

        for i in scramble_data:
            block = orig_img.crop(
                (i.dest_x, i.dest_y, i.dest_x + i.width, i.dest_y + i.height))
            dest_img.paste(block, (i.src_x, i.src_y))

        orig_img.close()
        img_remove_dummy = dest_img.crop((0, 0, width - dummy_pixels[0], height - dummy_pixels[1]))

        out_img = BytesIO()
        img_remove_dummy.save(out_img, 'PNG')

        return out_img.getvalue()
