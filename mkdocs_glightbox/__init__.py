from copyreg import constructor
import os
import logging
from mkdocs import utils
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
import re
from bs4 import BeautifulSoup
import json

log = logging.getLogger(__name__)
base_path = os.path.dirname(os.path.abspath(__file__))


class LightboxPlugin(BasePlugin):
    """ Add lightbox to MkDocs """

    config_scheme = (
        ("touchNavigation", config_options.Type(bool, default=False)),
        ("loop", config_options.Type(bool, default=False)),
        ("effect", config_options.Type(str, default="zoom")),
        ("width", config_options.Type(str, default="100%")),
        ("height", config_options.Type(str, default="auto")),
        ("zoomable", config_options.Type(bool, default=True)),
        ("draggable", config_options.Type(bool, default=True)),
    )

    def on_post_page(self, output, page, config, **kwargs):
        """ Add css link tag, javascript script tag, and javascript code to initialize GLightbox """

        soup = BeautifulSoup(output, "html.parser")

        css_link = soup.new_tag("link")
        css_link.attrs["href"] = os.path.join(
            config["site_url"], "assets/stylesheets/glightbox.min.css")
        css_link.attrs["rel"] = "stylesheet"
        soup.head.append(css_link)

        js_script = soup.new_tag("script")
        js_script.attrs["src"] = os.path.join(
            config["site_url"], "assets/javascripts/glightbox.min.js")
        soup.head.append(js_script)

        js_code = soup.new_tag("script")
        js_code["type"] = "text/javascript"
        lb_config = dict(self.config)
        lb_config = {k: lb_config[k] for k in ["touchNavigation", "loop"]}
        js_code.string = f"const lightbox = GLightbox({json.dumps(lb_config)});"
        soup.body.append(js_code)

        return str(soup)

    def on_page_content(self, html, page, config, **kwargs):
        """ Wrap img tag with archive tag with glightbox class and attributes from config """

        lb_data_config = dict(self.config)
        lb_data_config = {k: lb_data_config[k] for k in [
            "effect", "width", "height", "zoomable", "draggable"]}
        soup = BeautifulSoup(html, "html.parser")
        imgs = soup.find_all("img")
        for img in imgs:
            a = soup.new_tag("a")
            a["class"] = "glightbox"
            a["href"] = img.get("src", "")
            for key, val in lb_data_config.items():
                a[f"data-{key}"] = val
            img.wrap(a)
        return str(soup)

    def on_post_build(self, config, **kwargs):
        """ Copy glightbox"s css and js files to assets directory """

        output_base_path = os.path.join(config["site_dir"], "assets")
        css_path = os.path.join(output_base_path, "stylesheets")
        utils.copy_file(os.path.join(base_path, "glightbox/glightbox.min.css"), os.path.join(
            css_path, "glightbox.min.css"))
        js_path = os.path.join(output_base_path, "javascripts")
        utils.copy_file(os.path.join(base_path, "glightbox/glightbox.min.js"), os.path.join(
            js_path, "glightbox.min.js"))
