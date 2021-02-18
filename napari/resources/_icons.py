import re
from functools import lru_cache
from pathlib import Path

ICON_PATH = (Path(__file__).parent / 'icons').resolve()
ICONS = {x.stem: str(x) for x in ICON_PATH.iterdir() if x.suffix == '.svg'}


def get_icon_path(name: str) -> str:
    """Return path to an SVG in the theme icons."""
    if name not in ICONS:
        raise ValueError(
            f"unrecognized icon name: {name!r}. Known names: {ICONS}"
        )
    return ICONS[name]


svg_elem = re.compile(r'(<svg[^>]*>)')
svg_style = """<style type="text/css">
path {{fill: {0}; opacity: {1};}}
polygon {{fill: {0}; opacity: {1};}}
circle {{fill: {0}; opacity: {1};}}
rect {{fill: {0}; opacity: {1};}}
</style>"""


@lru_cache()
def get_raw_svg(path: str) -> str:
    """Get and cached SVG XML.

    Raises
    ------
    ValueError
        If the path exists but does not contain valid SVG data.
    """
    with open(path) as f:
        xml = f.read()
        if not svg_elem.search(xml):
            raise ValueError(f"Could not detect svg tag in {path!r}")
        return xml


@lru_cache()
def get_colorized_svg(path_or_xml: str, color: str = None, opacity=1) -> str:
    """Return a colorized version of the SVG XML at ``path``."""
    if '</svg>' in path_or_xml:
        xml = path_or_xml
    else:
        xml = get_raw_svg(path_or_xml)
    if not color:
        return xml

    # use regex to find the svg tag and insert css right after
    # (the '\\1' syntax includes the matched tag in the output)
    return svg_elem.sub(f'\\1{svg_style.format(color, opacity)}', xml)
