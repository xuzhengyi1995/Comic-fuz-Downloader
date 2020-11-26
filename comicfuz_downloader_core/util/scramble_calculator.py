__all__ = (
    'ScrambleCalculator',
    'ScrambleBlockInfo',
)

from typing import List, NamedTuple

from cachetools import LRUCache

from ..constant import *
from ..definition import *

scramble_data_cache = LRUCache(maxsize=256)


class ScrambleBlockInfo(NamedTuple):
    """
    Records the source and destination region of a single block in the image.
    `Source` is assumed to be the original image and `Destination` is the scrambled image.
    """
    src_x: int
    src_y: int
    dest_x: int
    dest_y: int
    width: int
    height: int


class ScrambleCalculator:
    # A constant in the JavaScript code of ComicFuz
    NFBR_A0X_A3H = 4

    @classmethod
    def pattern(cls, file_item: ComicFuzFileItem) -> int:
        """
        Calculate `Pattern` of a file. Used in later phases.
        """
        hash_message = str(file_item.file_path) + '/' + str(file_item.page_no)
        char_sum = sum(ord(c) for c in hash_message)
        return char_sum % cls.NFBR_A0X_A3H + 1

    @classmethod
    def get_scramble_data(
            cls, width: int, height: int, pattern: int,
            block_width: int = BLOCK_SIZE, block_height: int = BLOCK_SIZE,
    ) -> List[ScrambleBlockInfo]:
        """
        Calculate how the scrambling is done. The result is in terms of List[ScrambleBlockInfo].
        """
        # Find cache
        cache_key = (width, height, pattern, block_width, block_height)
        cache = scramble_data_cache.get(cache_key, default=None)
        if cache is not None:
            return cache

        y = width // block_width
        g = height // block_height
        f = width % block_width
        b = height % block_height
        result: List[ScrambleBlockInfo] = []

        s = y - 43 * pattern % y
        if s % y == 0:
            s = (y - 4) % y
        if s == 0:
            s = y - 1

        a = g - 47 * pattern % g
        if a % g == 0:
            a = g - 4
        if a == 0:
            a = g - 1

        if f > 0 and b > 0:
            o = s * block_width
            u = a * block_height
            result.append(ScrambleBlockInfo(
                src_x=o,
                src_y=u,
                dest_x=o,
                dest_y=u,
                width=f,
                height=b,
            ))

        if b > 0:
            for l in range(y):
                d = cls.__calc_x_coordinate_x_rest(l, y, pattern)
                h = cls.__calc_y_coordinate_x_rest(d, s, a, g, pattern)
                c = cls.__calc_position_with_rest(d, s, f, block_width)
                p = h * block_height
                o = cls.__calc_position_with_rest(l, s, f, block_width)
                u = a * block_height

                result.append(ScrambleBlockInfo(
                    src_x=o,
                    src_y=u,
                    dest_x=c,
                    dest_y=p,
                    width=block_width,
                    height=b,
                ))

        if f > 0:
            for m in range(g):
                h = cls.__calc_y_coordinate_y_rest(m, g, pattern)
                d = cls.__calc_x_coordinate_y_rest(h, s, a, y, pattern)
                c = d * block_width
                p = cls.__calc_position_with_rest(h, a, b, block_height)
                o = s * block_width
                u = cls.__calc_position_with_rest(m, a, b, block_height)

                result.append(ScrambleBlockInfo(
                    src_x=o,
                    src_y=u,
                    dest_x=c,
                    dest_y=p,
                    width=f,
                    height=block_height,
                ))

        for l in range(y):
            for m in range(g):
                d = (l + 29 * pattern + 31 * m) % y
                h = (m + 37 * pattern + 41 * d) % g
                c = d * block_width
                if d >= cls.__calc_x_coordinate_y_rest(h, s, a, y, pattern):
                    c += f
                p = h * block_height
                if h >= cls.__calc_y_coordinate_x_rest(d, s, a, g, pattern):
                    p += b
                o = l * block_width
                if l >= s:
                    o += f
                u = m * block_height
                if m >= a:
                    u += b

                result.append(ScrambleBlockInfo(
                    src_x=o,
                    src_y=u,
                    dest_x=c,
                    dest_y=p,
                    width=block_width,
                    height=block_height,
                ))

        scramble_data_cache[cache_key] = result
        return result

    @classmethod
    def __calc_position_with_rest(cls, e: int, t: int, r: int, i: int) -> int:
        if e >= t:
            return e * i + r
        return e * i

    @classmethod
    def __calc_x_coordinate_x_rest(cls, e: int, t: int, r: int) -> int:
        return (e + 61 * r) % t

    @classmethod
    def __calc_y_coordinate_x_rest(cls, e: int, t: int, r: int, i: int, n: int) -> int:
        if e < t:
            if n % 2 == 1:
                a = r
                s = 0
            else:
                a = i - r
                s = r
        else:
            if n % 2 != 1:
                a = r
                s = 0
            else:
                a = i - r
                s = r
        return (e + 53 * n + 59 * r) % a + s

    @classmethod
    def __calc_x_coordinate_y_rest(cls, e: int, t: int, r: int, i: int, n: int) -> int:
        if e < r:
            if n % 2 == 1:
                a = i - t
                s = t
            else:
                a = t
                s = 0
        else:
            if n % 2 != 1:
                a = i - t
                s = t
            else:
                a = t
                s = 0
        return (e + 67 * n + t + 71) % a + s

    @classmethod
    def __calc_y_coordinate_y_rest(cls, e: int, t: int, r: int) -> int:
        return (e + 73 * r) % t
