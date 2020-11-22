__all__ = (
    'PathUtil',
)


class PathUtil:
    SPECIAL_CHAR = ('<', '>', ':', '"', '/', '\\', '|', '?', '*')

    @classmethod
    def strip_bad_char(cls, path: str) -> str:
        for i in cls.SPECIAL_CHAR:
            path = path.replace(i, '_')

        return path
