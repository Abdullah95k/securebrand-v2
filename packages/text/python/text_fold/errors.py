"""TextError: what the fold refuses, with a code a caller can branch on."""

from typing import Literal

type TextErrorCode = Literal["not_string", "no_lang", "bad_lang", "not_unicode", "unicode_version"]


class TextError(Exception):
    """A refused input or runtime. `code` is one of not_string, no_lang, bad_lang, not_unicode
    (D8) and unicode_version (D-2). The message never quotes the text, which may be a person's
    words."""

    code: TextErrorCode

    def __init__(self, code: TextErrorCode, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
