import json
import logging
import os

from mkdocs import utils
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from selectolax.lexbor import LexborHTMLParser, create_tag

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
        ("width", config_options.Type(str, default="auto")),
        ("height", config_options.Type(str, default="auto")),
        ("zoomable", config_options.Type(bool, default=True)),
        ("draggable", config_options.Type(bool, default=True)),
        ("skip_classes", config_options.Type(list, default=[])),
        ("auto_themed", config_options.Type(bool, default=False)),
        ("auto_caption", config_options.Type(bool, default=False)),
        (
            "caption_position",
            config_options.Choice(("bottom", "top", "left", "right"), default="bottom"),
        ),
        ("background", config_options.Type(str, default="white")),
        ("shadow", config_options.Type(bool, default=True)),
        ("manual", config_options.Type(bool, default=False)),
    )

    def on_config(self, config):
        self.using_material = config["theme"].name == "material"
        self.using_material_privacy = (
            self.using_material
            and "material/privacy" in config["plugins"]
            and config["plugins"]["material/privacy"].config.enabled
        )

    def on_post_page(self, output, page, config, **kwargs):
        """Add css link tag, javascript script tag, and javascript code to initialize GLightbox"""
        # skip page with meta glightbox is false
        if "glightbox" in page.meta and page.meta.get("glightbox", True) is False:
            return output

        tree = LexborHTMLParser(output)
        head_node = tree.css_first("head")
        body_node = tree.css_first("body")

        glightbox_css_node = create_tag("link")
        glightbox_css_node.attrs["href"] = utils.get_relative_url(
            utils.normalize_url("assets/stylesheets/glightbox.min.css"), page.url
        )
        glightbox_css_node.attrs["rel"] = "stylesheet"

        glightbox_js_node = create_tag("script")
        glightbox_js_node.attrs["src"] = utils.get_relative_url(
            utils.normalize_url("assets/javascripts/glightbox.min.js"), page.url
        )
        head_node.insert_child(glightbox_css_node)
        head_node.insert_child(glightbox_js_node)

        css_text = (
            """
            html.glightbox-open { overflow: initial; height: 100%; }
            .gslide-title { margin-top: 0px; user-select: text; }
            .gslide-desc { color: #666; user-select: text; }
            .gslide-image img { background: """
            + self.config["background"]
            + """; }"""
        )
        if not self.config["shadow"]:
            css_text += """
            .glightbox-clean .gslide-media { -webkit-box-shadow: none; box-shadow: none; }"""
        if config["theme"].name == "material":
            css_text += """
            .gscrollbar-fixer { padding-right: 15px; }
            .gdesc-inner { font-size: 0.75rem; }
            body[data-md-color-scheme="slate"] .gdesc-inner { background: var(--md-default-bg-color); }
            body[data-md-color-scheme="slate"] .gslide-title { color: var(--md-default-fg-color); }
            body[data-md-color-scheme="slate"] .gslide-desc { color: var(--md-default-fg-color); }"""

        patch_css_node = create_tag("style")
        patch_css_node.attrs["id"] = "glightbox-style"
        patch_css_node.insert_child(css_text + "\n        ")
        head_node.insert_child(patch_css_node)

        plugin_config = dict(self.config)
        lb = {
            k: plugin_config[k]
            for k in ["touchNavigation", "loop", "zoomable", "draggable"]
        }
        lb["openEffect"] = plugin_config.get("effect", "zoom")
        lb["closeEffect"] = plugin_config.get("effect", "zoom")
        lb["slideEffect"] = plugin_config.get("slide_effect", "slide")
        js_code = ""
        if self.using_material_privacy:
            js_code += """document.querySelectorAll('.glightbox').forEach(function(element) {
    try {
        var img = element.querySelector('img');
        if (img && img.src) {
            element.setAttribute('href', img.src);
        } else {
            console.log('No img element with src attribute found');
        }
    } catch (error) {
        console.log('Error:', error);
    }
});
"""
        js_code += "const lightbox = GLightbox(" + json.dumps(lb) + ");\n"
        if self.using_material or "navigation.instant" in config["theme"].get(
            "features", []
        ):
            js_code += "document$.subscribe(()=>{ lightbox.reload(); });\n"

        init_js_node = create_tag("script")
        init_js_node.attrs["id"] = "init-glightbox"
        init_js_node.insert_child(js_code)
        body_node.insert_child(init_js_node)

        return tree.html

    def on_page_content(self, html, page, config, **kwargs):
        """Wrap img tag with anchor tag with glightbox class and attributes from config"""
        # skip page with meta glightbox is false
        if "glightbox" in page.meta and page.meta.get("glightbox", True) is False:
            return html

        skip_classes = ["emojione", "twemoji", "gemoji", "off-glb"] + self.config[
            "skip_classes"
        ]
        return self.wrap_img_with_anchor_selectolax(
            html, plugin_config=self.config, meta=page.meta, skip_classes=skip_classes
        )

    def wrap_img_with_anchor_selectolax(
        self, html: str, plugin_config, meta, skip_classes
    ):
        tree = LexborHTMLParser(html)

        for img in tree.css("img"):
            if self._should_skip_img(img, skip_classes, plugin_config, meta):
                continue

            attrs = self._build_anchor_attrs(img, plugin_config, meta)

            a_node = create_tag("a")
            for key, value in attrs.items():
                a_node.attrs[key] = str(value)

            img_clone = img
            a_node.insert_child(img_clone)
            img.replace_with(a_node)

        return tree.html

    def _should_skip_img(self, img, skip_classes, plugin_config, meta):
        """Skip by class, page meta, or plugin config"""
        if img.parent and img.parent.tag == "a":
            return True
        classes = img.attributes.get("class", "").split()
        if set(classes) & set(skip_classes):
            return True
        if plugin_config.get("manual") and meta.get("glightbox", None) is True:
            return False
        elif (
            meta.get("glightbox-manual", False) or plugin_config.get("manual")
        ) and "on-glb" not in classes:
            return True

    def _build_anchor_attrs(self, img, plugin_config, meta):
        """Get attributes from img for the anchor tag"""
        attrs = {
            "class": "glightbox",
            "data-type": "image",
            "data-width": plugin_config.get("width", "auto"),
            "data-height": plugin_config.get("height", "auto"),
        }

        if not self.using_material_privacy:
            attrs["href"] = img.attributes.get("src", "")

        auto_caption = self.config.get("auto_caption") or meta.get(
            "glightbox.auto_caption", False
        )

        slide_options_map = {
            "title": self._get_title_value,
            "description": self._get_description_value,
            "caption-position": self._get_caption_position_value,
            "gallery": self._get_gallery_value,
        }

        for option, value_getter in slide_options_map.items():
            attr = f"data-{option}"
            val = value_getter(img, auto_caption)

            if val:
                if attr == "data-caption-position":
                    attrs["data-desc-position"] = val
                else:
                    attrs[attr] = val

        return attrs

    def _get_title_value(self, img, auto_caption):
        val = img.attributes.get("data-title", "")
        if auto_caption and not val:
            val = img.attributes.get("alt", "")
        return val

    def _get_description_value(self, img, auto_caption):
        return img.attributes.get("data-description", "")

    def _get_caption_position_value(self, img, auto_caption):
        return img.attributes.get(
            "data-caption-position", self.config["caption_position"]
        )

    def _get_gallery_value(self, img, auto_caption):
        if self.config["auto_themed"]:
            if "#only-light" in img.attributes.get(
                "src", ""
            ) or "#gh-light-mode-only" in img.attributes.get("src", ""):
                return "light"
            elif "#only-dark" in img.attributes.get(
                "src", ""
            ) or "#gh-dark-mode-only" in img.attributes.get("src", ""):
                return "dark"
        return img.attributes.get("data-gallery", "")

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
