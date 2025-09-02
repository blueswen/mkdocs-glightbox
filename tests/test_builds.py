# standard lib
import logging
import os
import re
import shutil

# other 3rd party
import pytest
from click.testing import CliRunner

# MkDocs
from mkdocs.__main__ import build_command
from selectolax.lexbor import LexborHTMLParser

# ##################################
# ######## Globals #################
# ##################################

# custom log level to get plugin info messages
logging.basicConfig(level=logging.INFO)

# ##################################
# ########## Helpers ###############
# ##################################


def setup_clean_mkdocs_folder(
    mkdocs_yml_path: str, output_path: str, docs_path: str = "tests/fixtures/docs"
):
    """
    Sets up a clean mkdocs directory
    outputpath/testproject
    ├── docs/
    └── mkdocs.yml
    Args:
        mkdocs_yml_path (Path): Path of mkdocs.yml file to use
        output_path (Path): Path of folder in which to create mkdocs project
    Returns:
        testproject_path (Path): Path to test project
    """

    testproject_path = output_path / "testproject"

    # Create empty 'testproject' folder
    if os.path.exists(str(testproject_path)):
        logging.warning(
            """This command does not work on windows.
        Refactor your test to use setup_clean_mkdocs_folder() only once"""
        )
        shutil.rmtree(str(testproject_path))

    # Copy correct mkdocs.yml file and our test 'docs/'
    shutil.copytree(docs_path, str(testproject_path / docs_path.split("/")[-1]))

    shutil.copyfile(mkdocs_yml_path, str(testproject_path / "mkdocs.yml"))

    return testproject_path


def build_docs_setup(testproject_path: str):
    """
    Runs the `mkdocs build` command
    Args:
        testproject_path (Path): Path to test project
    Returns:
        command: Object with results of command
    """

    # TODO: Try specifying path in CliRunner, this function could be one-liner
    cwd = os.getcwd()
    os.chdir(str(testproject_path))

    try:
        runner = CliRunner()
        run = runner.invoke(build_command)
        os.chdir(cwd)
        return run
    except:
        os.chdir(cwd)
        raise


def validate_build(testproject_path: str, plugin_config: dict = {}):
    """
    Validates a build from a testproject
    Args:
        testproject_path (Path): Path to test project
    """
    assert os.path.exists(str(testproject_path / "site"))

    # Make sure index file exists
    index_file = testproject_path / "site/index.html"
    assert index_file.exists(), "%s does not exist" % index_file


def validate_mkdocs_file(
    temp_path: str, mkdocs_yml_file: str, docs_path: str = "tests/fixtures/docs"
):
    """
    Creates a clean mkdocs project
    for a mkdocs YML file, builds and validates it.
    Args:
        temp_path (PosixPath): Path to temporary folder
        mkdocs_yml_file (PosixPath): Path to mkdocs.yml file
    """
    testproject_path = setup_clean_mkdocs_folder(
        mkdocs_yml_path=mkdocs_yml_file, output_path=temp_path, docs_path=docs_path
    )
    result = build_docs_setup(
        testproject_path,
    )
    assert result.exit_code == 0, "'mkdocs build' command failed"

    # validate build with locale retrieved from mkdocs config file
    validate_build(testproject_path)

    return testproject_path


def validate_static(tree: any, path: str = "", exist: bool = True):
    """
    Validate glightbox.min.css and glightbox.min.js have been loaded or not
    """
    head_content = tree.css_first("head").html
    assert exist == (
        re.search(
            rf'<link href="{re.escape(path)}assets\/stylesheets\/glightbox\.min\.css" rel="stylesheet">',
            head_content,
        )
        is not None
    )
    assert exist == (
        re.search(
            rf'<script src="{re.escape(path)}assets\/javascripts\/glightbox\.min\.js"><\/script>',
            head_content,
        )
        is not None
    )


def validate_script(tree: any, exist: bool = True):
    """
    Validate GLightbox have been initialized or not
    """
    body_content = tree.css_first("body").html
    assert exist == (
        re.search(
            r"const lightbox = GLightbox\((.*)\);",
            body_content,
        )
        is not None
    )


def get_init_script(soup):
    script = soup.find("script", id="init-glightbox")
    assert script, "init-glightbox <script> not found"
    return script


def assert_lightbox_wrap(img_selector, soup, href=None, **data_attrs):
    img = soup.select_one(img_selector)
    assert img, f"Could not find image matching {img_selector}"
    a = img.parent
    assert a.name == "a"
    assert "glightbox" in a.get("class", [])
    if href is not None:
        assert a["href"] == href
    for key, val in data_attrs.items():
        attr = f"{key}"
        assert a.get(attr) == val, f"{attr} != {val}"


def validate_lightbox_wrap(img, href=None, **data_attrs):
    a = img.parent
    assert a.tag == "a"
    assert "glightbox" in a.attrs.get("class", [])
    if href is not None:
        assert a.attrs.get("href") == href
    else:
        assert a.attrs.get("href") == img.attrs.get("src")
    for key, val in data_attrs.items():
        attr = f"{key}"
        assert a.attrs.get(attr) == val, f"{attr} != {val}"


def validate_lightbox_wrap_disable(img):
    parent = img.parent
    if parent.tag == "a":
        assert "glightbox" not in parent.attrs.get("class", [])
    else:
        assert parent.tag == "p"


EMOJI_LIST = ["emojione", "gemoji", "twemoji"]

# ##################################
# ########### Tests ################
# ##################################


def test_basic(tmp_path):
    """
    Minimal sample
    """
    mkdocs_file = "mkdocs.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree)
    validate_script(tree)
    validate_lightbox_wrap(tree.css_first("img[alt='image']"))
    validate_lightbox_wrap(tree.css_first("img[alt='img-tag']"))


def test_material(tmp_path):
    """
    Integrate with Material for MkDocs
    """
    mkdocs_file = "mkdocs-material.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree)
    validate_script(tree)
    script = tree.css_first("script#init-glightbox")
    assert "document$.subscribe(()=>{ lightbox.reload(); });" in script.text()
    validate_lightbox_wrap(tree.css_first("img[alt='image']"))


def test_material_instant(tmp_path):
    """
    Integrate with Material for MkDocs
    """
    mkdocs_file = "mkdocs-material-instant.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree)
    validate_script(tree)
    script = tree.css_first("script#init-glightbox")
    assert "document$.subscribe(()=>{ lightbox.reload(); });" in script.text()
    validate_lightbox_wrap(tree.css_first("img[alt='image']"))


def test_use_directory_urls(tmp_path):
    """
    Compatible with use_directory_urls is false or with --use-directory-urls and --use-directory-urls as args
    https://www.mkdocs.org/user-guide/configuration/#use_directory_urls
    https://www.mkdocs.org/user-guide/cli/
    """
    mkdocs_file = "mkdocs-target-file.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/sub_dir/page_in_sub_dir.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    validate_lightbox_wrap(tree.css_first("img[alt='image']"))


def test_disable_by_page(tmp_path):
    """
    Disable by page with page meta
    """
    mkdocs_file = "mkdocs.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/disable_by_page/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, exist=False)
    validate_script(tree, exist=False)
    for img in tree.css("img[alt='image']"):
        validate_lightbox_wrap_disable(img)


def test_disable_by_image(tmp_path):
    """
    Disable by the image with image custom class or predefined class
    """
    mkdocs_file = "mkdocs-disable-by-image.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/disable_by_image/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    for img in tree.css("img.off-glb,img.skip-lightbox"):
        validate_lightbox_wrap_disable(img)


@pytest.mark.parametrize("emoji_name", EMOJI_LIST)
def test_disable_with_emoji(emoji_name, tmp_path):
    """
    Disable when the image with emoji class name(defined in PyMdown Extensions): emojione, gemoji, twemoji
    https://facelessuser.github.io/pymdown-extensions/extensions/emoji/
    """
    mkdocs_file = f"mkdocs-material-{emoji_name}.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/emoji/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    for img in tree.css(f"img.{emoji_name}"):
        validate_lightbox_wrap_disable(img)


def test_url(tmp_path):
    """
    Compatible with URL
    """
    mkdocs_file = "mkdocs.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/url/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    validate_lightbox_wrap(tree.css_first("img[alt='image']"))


def test_default_options(tmp_path):
    """
    Validate GLightbox default options
    """
    mkdocs_file = "mkdocs.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/images/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    for img in tree.css("img[alt^='image-']"):
        validate_lightbox_wrap(img)

    javascript = tree.css_first("script#init-glightbox")
    assert javascript is not None
    javascript_text = javascript.text()
    assert "const lightbox = GLightbox(" in javascript_text
    options = [
        '"touchNavigation": true',
        '"loop": false',
        '"zoomable": true',
        '"draggable": true',
        '"openEffect": "zoom"',
        '"closeEffect": "zoom"',
        '"slideEffect": "slide"',
    ]
    for option in options:
        assert option in javascript_text


def test_options(tmp_path):
    """
    Validate GLightbox options setting through plugins
    """
    mkdocs_file = "mkdocs-options.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/images/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    # validate override style
    style = tree.css_first("style#glightbox-style")
    assert style is not None
    assert ".gslide-image img { background: none; }" in style.text()
    assert (
        ".glightbox-clean .gslide-media { -webkit-box-shadow: none; box-shadow: none; }"
        in style.text()
    )
    validate_lightbox_wrap(
        tree.css_first("img[alt='image-a']"),
        **{"data-desc-position": "right", "data-width": "80%", "data-height": "60%"},
    )

    # validate GLightbox init options
    javascript = tree.css_first("script#init-glightbox")
    assert javascript is not None
    javascript_text = javascript.text()
    for option in [
        '"touchNavigation": false',
        '"loop": true',
        '"zoomable": false',
        '"draggable": false',
        '"openEffect": "fade"',
        '"closeEffect": "fade"',
        '"slideEffect": "fade"',
    ]:
        assert option in javascript_text


def test_gallery(tmp_path):
    """
    Validate gallery
    """
    mkdocs_file = "mkdocs-material.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/gallery/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    for img in tree.css("img[alt='image-a'],img[alt='image-b']"):
        validate_lightbox_wrap(img, **{"data-gallery": "1"})
    for img in tree.css("img[alt='image-c'],img[alt='image-d']"):
        validate_lightbox_wrap(img, **{"data-gallery": "2"})


def test_caption(tmp_path):
    """
    Validate captions feature
    """
    mkdocs_file = "mkdocs-material.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/caption/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    validate_lightbox_wrap(
        tree.css_first("img[alt='image-default']"),
        **{"data-description": "data-description", "data-title": "data-title"},
    )
    validate_lightbox_wrap(
        tree.css_first("img[alt='image-right']"),
        **{
            "data-desc-position": "right",
            "data-description": "data-description",
            "data-title": "data-title",
        },
    )
    validate_lightbox_wrap(
        tree.css_first("img[alt='image-figure']"),
        **{"data-description": "data-description", "data-title": "data-title"},
    )


def test_auto_caption_by_page(tmp_path):
    """
    Validate auto captions with image tag alt by page
    """
    mkdocs_file = "mkdocs-material.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/auto_caption/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    validate_lightbox_wrap(
        tree.css_first("img[alt='alt as caption']"),
        **{"data-title": "alt as caption"},
    )


def test_auto_caption(tmp_path):
    """
    Validate auto captions with image tag alt for all page
    """
    mkdocs_file = "mkdocs-auto-caption.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree)
    validate_script(tree)
    validate_lightbox_wrap(
        tree.css_first("img[alt='image']"), **{"data-title": "image"}
    )


def test_material_template(tmp_path):
    """
    Compatible with template
    """
    mkdocs_file = "mkdocs-material-template.yml"
    testproject_path = validate_mkdocs_file(
        tmp_path,
        f"tests/fixtures/{mkdocs_file}",
        docs_path="tests/fixtures/template_docs",
    )
    file = testproject_path / "site/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree)
    validate_script(tree)
    script = tree.css_first("script#init-glightbox")
    assert "document$.subscribe(()=>{ lightbox.reload(); });" in script.text()
    validate_lightbox_wrap(tree.css_first("img[alt='image']"))


def test_site_url(tmp_path):
    """
    Compatible with the site with path prefix
    """
    mkdocs_file = "mkdocs-site-url.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree)
    validate_script(tree)
    validate_lightbox_wrap(tree.css_first("img[alt='image']"))

    file = testproject_path / "site/images/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    for img in tree.css("img[alt^='image-']"):
        validate_lightbox_wrap(img)


def test_static(tmp_path):
    """
    Validate static files
    """
    mkdocs_file = "mkdocs.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    assert os.path.exists(
        os.path.join(testproject_path, "site/assets/stylesheets/glightbox.min.css")
    )
    assert os.path.exists(
        os.path.join(testproject_path, "site/assets/javascripts/glightbox.min.js")
    )


def test_image_in_anchor(tmp_path):
    """
    Disable when image in an anchor tag
    """
    mkdocs_file = "mkdocs.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/image_in_anchor/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    validate_lightbox_wrap_disable(tree.css_first("img[alt='image-in-anchor']"))


def test_image_without_ext(tmp_path):
    """
    Image without extension
    """
    mkdocs_file = "mkdocs.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/without_ext/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    validate_lightbox_wrap(tree.css_first("img[alt='Image without extension']"))


def test_error(tmp_path):
    """
    Wrapping for error
    """
    mkdocs_file = "mkdocs-error.yml"
    testproject_path = validate_mkdocs_file(
        tmp_path,
        f"tests/fixtures/{mkdocs_file}",
        docs_path="tests/fixtures/error_docs",
    )
    file = testproject_path / "site/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree)
    validate_script(tree)


def test_privacy(tmp_path):
    """
    Compatible with material privacy plugin
    """
    mkdocs_file = "mkdocs-material-privacy.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/url/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    a = tree.css_first("img[alt='image']").parent
    assert a.tag == "a"
    assert "glightbox" in a.attrs.get("class", [])
    script = tree.css_first("script#init-glightbox")
    assert (
        "document.querySelectorAll('.glightbox').forEach(function(element)"
        in script.text()
    )


def test_enable_by_image(tmp_path):
    """
    Enable by the image with on-glb class
    """
    mkdocs_file = "mkdocs-material.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/enable_by_image/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    validate_lightbox_wrap(tree.css_first("img[alt='image-enable']"))
    validate_lightbox_wrap_disable(tree.css_first("img[alt='image-disable']"))


def test_manual(tmp_path):
    """
    Manual mode
    """
    mkdocs_file = "mkdocs-manual.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree)
    validate_script(tree)
    validate_lightbox_wrap_disable(tree.css_first("img[alt='image']"))

    file = testproject_path / "site/manual/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    validate_lightbox_wrap(tree.css_first("img[alt='image']"))

    file = testproject_path / "site/manual_enable_by_page/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    for img in tree.css("img[alt='image-a'],img[alt='image-c']"):
        validate_lightbox_wrap(img)
    validate_lightbox_wrap_disable(tree.css_first("img[alt='image-b']"))


def test_auto_theme(tmp_path):
    """
    Validate auto theme feature
    """
    mkdocs_file = "mkdocs-material-theme.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/theme/index.html"
    tree = LexborHTMLParser(file.read_text(encoding="utf8"))
    validate_static(tree, path="../")
    validate_script(tree)
    light_img_nodes = tree.css("img[alt='light']")
    assert len(light_img_nodes) > 0
    for light_img_node in light_img_nodes:
        validate_lightbox_wrap(light_img_node)
        assert light_img_node.parent.attrs.get("data-gallery") == "light"
    dark_img_nodes = tree.css("img[alt='dark']")
    assert len(dark_img_nodes) > 0
    for dark_img_node in dark_img_nodes:
        validate_lightbox_wrap(dark_img_node)
        assert dark_img_node.parent.attrs.get("data-gallery") == "dark"


@pytest.mark.timeout(5)  # prevent hanging indefinitely
def test_edge_cases(tmp_path):
    """
    Validate edge cases
    """
    mkdocs_file = "mkdocs-edge-cases.yml"
    validate_mkdocs_file(
        tmp_path,
        f"tests/fixtures/{mkdocs_file}",
        docs_path="tests/fixtures/edge_cases_docs",
    )
