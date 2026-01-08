from __future__ import annotations

from html import escape as html_escape

from .model import Description


_QTEXT_PREFIX = (
    '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
    '"http://www.w3.org/TR/REC-html40/strict.dtd">\n'
    '<html><head><meta name="qrichtext" content="1" />'
    '<style type="text/css">\n'
    "p, li { white-space: pre-wrap; }\n"
    "</style></head>"
    '<body style=" font-family:\'Roboto\'; ; font-weight:400; font-style:normal;">\n'
)

_QTEXT_SUFFIX = "</body></html>"


def _p(text: str) -> str:
    return (
        '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; '
        'margin-right:0px; -qt-block-indent:0; text-indent:0px;">'
        f"{text}</p>"
    )


def _empty_p() -> str:
    return (
        '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; '
        'margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">'
        "<br /></p>"
    )


def plain_to_qrich(text: str) -> str:
    t = text.strip("\n")
    if not t.strip():
        return _QTEXT_PREFIX + _empty_p() + _QTEXT_SUFFIX

    paragraphs: list[str] = []
    for para in t.split("\n\n"):
        lines = para.splitlines()
        safe = "<br />".join(html_escape(line, quote=False) for line in lines)
        paragraphs.append(_p(safe))

    return _QTEXT_PREFIX + "\n".join(paragraphs) + _QTEXT_SUFFIX


def description_to_qrich(desc: Description) -> str:
    if desc.format == "qrich":
        return desc.text
    return plain_to_qrich(desc.text)


