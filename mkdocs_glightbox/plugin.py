import json
import logging
import os
import re

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

        # Define regular expressions for matching the relevant sections of the HTML code
        head_regex = re.compile(r"<head>(.*?)<\/head>", flags=re.DOTALL)
        body_regex = re.compile(r"<body(.*?)<\/body>", flags=re.DOTALL)

        # Modify the CSS link
        css_link = f'<link href="{utils.get_relative_url(utils.normalize_url("assets/stylesheets/glightbox.min.css"), page.url)}" rel="stylesheet"/>'
        output = head_regex.sub(f"<head>\\1 {css_link}</head>", output)

        # Modify the CSS patch
        css_patch = """
    html.glightbox-open { overflow: initial; height: 100%; }
    .gslide-title { margin-top: 0px; user-select: text; }
    .gslide-desc { color: #666; user-select: text; }"""
        css_patch += f"""
    .gslide-image img {{ background: {self.config['background']}; }}"""
        if not self.config["shadow"]:
            css_patch += """
    .glightbox-clean .gslide-media {
        -webkit-box-shadow: none;
        box-shadow: none;
    }"""
        if config["theme"].name == "material":
            css_patch += """
    .gscrollbar-fixer { padding-right: 15px; }
    .gdesc-inner { font-size: 0.75rem; }
    body[data-md-color-scheme="slate"] .gdesc-inner { background: var(--md-default-bg-color);}
    body[data-md-color-scheme="slate"] .gslide-title { color: var(--md-default-fg-color);}
    body[data-md-color-scheme="slate"] .gslide-desc { color: var(--md-default-fg-color);}"""
        output = head_regex.sub(f"<head>\\1<style>{css_patch}</style></head>", output)

        # Modify the JS script
        js_script = f'<script src="{utils.get_relative_url(utils.normalize_url("assets/javascripts/glightbox.min.js"), page.url)}"></script>'
        output = head_regex.sub(f"<head>\\1 {js_script}</head>", output)

        # Modify the JS code
        plugin_config = dict(self.config)
        lb_config = {
            k: plugin_config[k]
            for k in ["touchNavigation", "loop", "zoomable", "draggable"]
        }
        lb_config["openEffect"] = plugin_config.get("effect", "zoom")
        lb_config["closeEffect"] = plugin_config.get("effect", "zoom")
        lb_config["slideEffect"] = plugin_config.get("slide_effect", "slide")
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
        js_code += f"const lightbox = GLightbox({json.dumps(lb_config)});\n"
        if self.using_material or "navigation.instant" in config["theme"].get(
            "features", []
        ):
            # support compatible with mkdocs-material Instant loading feature
            js_code += "document$.subscribe(() => { lightbox.reload() });\n"
        output = body_regex.sub(
            f'<body\\1<script id="init-glightbox">{js_code}</script></body>', output
        )

        return output

    def on_page_markdown(self, markdown, page, config, files, **kwargs):
        """Support the #only-dark feature by setting the data-gallery property"""
        if not self.config["auto_themed"] or not page.meta.get("glightbox.auto_themed", True):
            return markdown

        markdown = re.sub("!\\[[^\\]]*\\]\\([^)]*\\)", self.repl_md, markdown)
        markdown = re.sub("<img\\s+[^>]*>", self.repl_html, markdown)

        return markdown

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

        # Use regex to find image tags that need to be wrapped with anchor tags and image tags already wrapped with anchor tags
        pattern = re.compile(
            r"<a\b[^>]*>(?:\s*<[^>]+>\s*)*<img\b[^>]*>(?:\s*<[^>]+>\s*)*</a>|<img(?P<attr>.*?)>"
        )
        html = pattern.sub(
            lambda match: self.wrap_img_with_anchor(
                match, plugin_config, skip_class, page.meta
            ),
            html,
        )

        return html

    @staticmethod
    def repl_md(match):
        """Add attribute data-gallery to the img tag (type: md)"""
        md = match.group()
        if "#only-light" in md or "#gh-light-mode-only" in md:
            return md + "{data-gallery='light'}"
        elif "#only-dark" in md or "#gh-dark-mode-only" in md:
            return md + "{data-gallery='dark'}"
        return md

    @staticmethod
    def repl_html(match):
        """Add attribute data-gallery to the img tag (type: html)"""
        html = match.group()
        if "#only-light" in html or "#gh-light-mode-only" in html:
            return f'{html[:4]} data-gallery="light" {html[4:]}'
        elif "#only-dark" in html or "#gh-dark-mode-only" in html:
            return f'{html[:4]} data-gallery="dark" {html[4:]}'
        return html

    def wrap_img_with_anchor(self, match, plugin_config, skip_class, meta):
        """Wrap image tags with anchor tags"""
        try:
            a_pattern = re.compile(r"<a(?P<attr>.*?)>")
            if a_pattern.match(match.group(0)):
                return match.group(0)

            img_tag = match.group(0)
            img_attr = match.group("attr")
            classes = re.findall(r'class="([^"]+)"', img_attr)
            classes = [c for match in classes for c in match.split()]

            if self.config["manual"] and meta.get("glightbox", None) is True:
                # with manual mode but enable glightbox in page meta
                if set(skip_class) & set(classes):
                    # skip image with off-glb and specific class
                    return img_tag
            elif meta.get("glightbox-manual", False) or self.config["manual"]:
                # disable by page meta or global config
                if "on-glb" not in classes:
                    # skip image without on-glb class
                    return img_tag
            elif set(skip_class) & set(classes):
                # skip image with off-glb and specific class
                return img_tag

            if self.using_material_privacy:
                # skip href attribute if using material privacy plugin, will be set by js code
                a_tag = '<a class="glightbox" data-type="image"'
            else:
                src = re.search(r"src=[\"\']([^\"\']+)", img_attr).group(1)
                a_tag = f'<a class="glightbox" href="{src}" data-type="image"'
            # setting data-width and data-height with plugin options
            for k, v in plugin_config.items():
                a_tag += f' data-{k}="{v}"'
            slide_options = [
                "title",
                "description",
                "caption-position",
                "gallery",
            ]
            for option in slide_options:
                attr = f"data-{option}"
                if attr == "data-title":
                    val = re.search(r"data-title=[\"]([^\"]+)", img_attr)
                    if self.config["auto_caption"] or (
                        "glightbox.auto_caption" in meta
                        and meta.get("glightbox.auto_caption", False) is True
                    ):
                        if val:
                            val = val.group(1)
                        else:
                            val = re.search(r"alt=[\"]([^\"]+)", img_attr)
                            val = val.group(1) if val else ""
                    else:
                        val = val.group(1) if val else ""
                elif attr == "data-caption-position":
                    val = re.search(r"data-caption-position=[\"]([^\"]+)", img_attr)
                    val = val.group(1) if val else self.config["caption_position"]
                else:
                    val = re.search(f'{attr}=["]([^"]+)', img_attr)
                    val = val.group(1) if val else ""

                # skip val is empty
                if val != "":
                    # convert data-caption-position to data-desc-position
                    if attr == "data-caption-position":
                        a_tag += f' data-desc-position="{val}"'
                    else:
                        a_tag += f' {attr}="{val}"'
            a_tag += f">{img_tag}</a>"
            return a_tag
        except Exception as e:
            log.warning(
                f"Error in wrapping img tag with anchor tag: {e} {match.group(0)}"
            )
            return match.group(0)

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
