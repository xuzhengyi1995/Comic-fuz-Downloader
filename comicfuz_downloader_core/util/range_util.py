__all__ = (
    'RangeUtil',
)

import re
from itertools import islice
from typing import Sequence, Tuple, List

RE_SPACE = re.compile(r'\s+')


class RangeUtil:
    @staticmethod
    def merge_ranges(
            ranges: Sequence[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        """
        Merge right-open ranges.
        """
        ranges = sorted(ranges, key=lambda x: x[0])
        if len(ranges) == 0:
            return []

        last_a, last_b = ranges[0]
        result: List[Tuple[int, int]] = []

        for a, b in islice(ranges, 1, None):
            if a <= last_b:
                last_b = max(b, last_b)
            else:
                result.append((last_a, last_b))
                last_a, last_b = a, b

        result.append((last_a, last_b))
        return result

    @staticmethod
    def parse_range_string(
            range_str: str, right_open: bool, bounding_range: Tuple[int, int] = None
    ) -> List[Tuple[int, int]]:
        """
        Parse range string like `1, 2-3,4-6` into list of tuples.
        You need to specify whether range in `range_str` is right-open or fully closed.

        WARNING: The bounding range is always assumed to be right-open even if `right_open` is False, and return values
            are always right-open ranges.
        """
        range_str = RE_SPACE.sub('', range_str)
        range_items = range_str.split(',')
        ranges_result: List[Tuple[int, int]] = []

        bound_a, bound_b = 0, 0  # Fuck warnings
        if bounding_range is not None:
            bound_a, bound_b = bounding_range

        for item in range_items:
            if '-' in item:
                a_str, b_str = item.split('-')
                a, b = int(a_str), int(b_str)
            else:
                a = int(item)
                b = a

            if a > b:
                a, b = b, a

            # Convert to right-open range
            if not right_open:
                b += 1

            if bounding_range is not None:
                if a < bound_a:
                    a = bound_a
                if b > bound_b:
                    b = bound_b

            ranges_result.append((a, b))

        ranges_result = RangeUtil.merge_ranges(ranges_result)
        return ranges_result
