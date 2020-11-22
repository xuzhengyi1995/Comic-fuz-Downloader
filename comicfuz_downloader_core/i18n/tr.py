__all__ = (
    'tr', 'I18nUtil',
)

from ..constant import *

curr_language = LANGUAGES[DEFAULT_LANGUAGE]


def tr(x: str) -> str:
    result = curr_language.get(x, None)
    if result is None:
        return x

    return result


class I18nUtil:
    @staticmethod
    def set_language(x: str) -> None:
        global curr_language
        if x not in LANGUAGES:
            x = DEFAULT_LANGUAGE
        curr_language = LANGUAGES[x]
