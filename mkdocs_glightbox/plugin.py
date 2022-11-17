import json
import logging
import os

from bs4 import BeautifulSoup
from mkdocs import utils
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

log = logging.getLogger(__name__)
base_path = os.path.dirname(os.path.abspath(__file__))


class LightboxPlugin(BasePlugin):
    """Add lightbox to MkDocs"""

    config_scheme = (
        ("touchNavigation", config_options.Type(bool, default=True)),
        ("loop", config_options.Type(bool, default=False)),
        ("effect", config_options.Choice(("zoom", "fade", "none"), default="zoom")),
        (
            "slide_effect",
            config_options.Choice(("slide", "zoom", "fade", "none"), default="slide"),
        ),
        ("width", config_options.Type(str, default="100%")),
        ("height", config_options.Type(str, default="auto")),
        ("zoomable", config_options.Type(bool, default=True)),
        ("draggable", config_options.Type(bool, default=True)),
        ("skip_classes", config_options.Type(list, default=[])),
        ("auto_caption", config_options.Type(bool, default=False)),
        (
            "caption_position",
            config_options.Choice(("bottom", "top", "left", "right"), default="bottom"),
        ),
    )

    def on_post_page(self, output, page, config, **kwargs):
        """Add css link tag, javascript script tag, and javascript code to initialize GLightbox"""
        # skip page with meta glightbox is false
        if "glightbox" in page.meta and page.meta.get("glightbox", True) is False:
            return output

        soup = BeautifulSoup(output, "html.parser")

        if soup.head:
            css_link = soup.new_tag("link")
            css_link.attrs["href"] = utils.get_relative_url(
                utils.normalize_url("assets/stylesheets/glightbox.min.css"), page.url
            )
            css_link.attrs["rel"] = "stylesheet"
            soup.head.append(css_link)

            css_patch = soup.new_tag("style")
            css_patch.string = """
            html.glightbox-open { overflow: initial; height: 100%; }
            .gslide-title { margin-top: 0px; user-select: text; }
            .gslide-desc { color: #666; user-select: text; }
            .gslide-image img { background: white; }
            """
            if config["theme"].name == "material":
                css_patch.string += """
                .gscrollbar-fixer { padding-right: 15px; }
                .gdesc-inner { font-size: 0.75rem; }
                body[data-md-color-scheme="slate"] .gdesc-inner { background: var(--md-default-bg-color);}
                body[data-md-color-scheme="slate"] .gslide-title { color: var(--md-default-fg-color);}
                body[data-md-color-scheme="slate"] .gslide-desc { color: var(--md-default-fg-color);}
                """
            soup.head.append(css_patch)

            js_script = soup.new_tag("script")
            js_script.attrs["src"] = utils.get_relative_url(
                utils.normalize_url("assets/javascripts/glightbox.min.js"), page.url
            )
            soup.head.append(js_script)

            js_code = soup.new_tag("script")
            plugin_config = dict(self.config)
            lb_config = {
                k: plugin_config[k]
                for k in ["touchNavigation", "loop", "zoomable", "draggable"]
            }
            lb_config["openEffect"] = plugin_config.get("effect", "zoom")
            lb_config["closeEffect"] = plugin_config.get("effect", "zoom")
            lb_config["slideEffect"] = plugin_config.get("slide_effect", "slide")
            js_code.string = f"const lightbox = GLightbox({json.dumps(lb_config)});"
            if config["theme"].name == "material" or "navigation.instant" in config[
                "theme"
            ]._vars.get("features", []):
                # support compatible with mkdocs-material Instant loading feature
                js_code.string = "document$.subscribe(() => {" + js_code.string + "})"
            soup.body.append(js_code)

        return str(soup)

    def on_page_content(self, html, page, config, **kwargs):
        """Wrap img tag with anchor tag with glightbox class and attributes from config"""
        # skip page with meta glightbox is false
        if "glightbox" in page.meta and page.meta.get("glightbox", True) is False:
            return html
        plugin_config = {k: dict(self.config)[k] for k in ["width", "height"]}
        # skip emoji img with index as class name from pymdownx.emoji https://facelessuser.github.io/pymdown-extensions/extensions/emoji/
        skip_class = ["emojione", "twemoji", "gemoji"]
        # skip image with off-glb and specific class
        skip_class += ["off-glb"] + self.config["skip_classes"]
        soup = BeautifulSoup(html, "html.parser")
        imgs = soup.find_all("img")
        for img in imgs:
            if set(skip_class) & set(img.get("class", [])) or img.parent.name == "a":
                continue
            a = soup.new_tag("a")
            a["class"] = "glightbox"
            a["href"] = img.get("src", "")
            # setting data-width and data-height with plugin options
            for k, v in plugin_config.items():
                a[f"data-{k}"] = v
            slide_options = ["title", "description", "caption-position", "gallery"]
            for option in slide_options:
                attr = f"data-{option}"
                if attr == "data-title":
                    # alt as title when auto_caption is enabled
                    if self.config["auto_caption"] or (
                        "glightbox.auto_caption" in page.meta
                        and page.meta.get("glightbox.auto_caption", False) is True
                    ):
                        val = img.get("data-title", img.get("alt", ""))
                    else:
                        val = img.get("data-title", "")
                elif attr == "data-caption-position":
                    # plugin option caption_position as default
                    val = img.get(
                        "data-caption-position", self.config["caption_position"]
                    )
                else:
                    val = img.get(attr, "")

                # skip val is empty
                if val != "":
                    # convert data-caption-position to data-desc-position
                    if attr == "data-caption-position":
                        a["data-desc-position"] = val
                    else:
                        a[attr] = val
            img.wrap(a)
        return str(soup)

    def on_post_build(self, config, **kwargs):
        """Copy glightbox"s css and js files to assets directory"""

        output_base_path = os.path.join(config["site_dir"], "assets")
        css_path = os.path.join(output_base_path, "stylesheets")
        utils.copy_file(
            os.path.join(base_path, "glightbox", "glightbox.min.css"),
            os.path.join(css_path, "glightbox.min.css"),
        )
        js_path = os.path.join(output_base_path, "javascripts")
        utils.copy_file(
            os.path.join(base_path, "glightbox", "glightbox.min.js"),
            os.path.join(js_path, "glightbox.min.js"),
        )
