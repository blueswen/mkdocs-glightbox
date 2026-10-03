from types import SimpleNamespace

import pytest
from selectolax.lexbor import LexborHTMLParser

from mkdocs_glightbox.plugin import LightboxPlugin


@pytest.mark.parametrize(
    "image_html",
    [
        '<img src="image.png" alt="linked">',
        '<span><img src="image.png" alt="linked"></span>',
        '<span><em><img src="image.png" alt="linked"></em></span>',
        '<picture><source srcset="image.webp"><img src="image.png" alt="linked"></picture>',
    ],
)
def test_images_inside_existing_links_are_not_wrapped(image_html):
    plugin = LightboxPlugin()
    plugin.load_config({})
    plugin.using_material_privacy = False
    html = '<a href="destination.html">' + image_html + '</a>'

    output = plugin.on_page_content(html, SimpleNamespace(meta={}), {})
    tree = LexborHTMLParser(output)

    assert len(tree.css("a")) == 1
    assert tree.css_first("a").attrs["href"] == "destination.html"
    assert not tree.css("a.glightbox")
    assert tree.css_first('img[alt="linked"]') is not None


def test_unlinked_image_inside_container_is_still_wrapped():
    plugin = LightboxPlugin()
    plugin.load_config({})
    plugin.using_material_privacy = False

    output = plugin.on_page_content(
        '<span><img src="image.png" alt="unlinked"></span>',
        SimpleNamespace(meta={}),
        {},
    )
    tree = LexborHTMLParser(output)

    anchor = tree.css_first("span > a.glightbox")
    assert anchor is not None
    assert anchor.attrs["href"] == "image.png"
    assert anchor.css_first('img[alt="unlinked"]') is not None
