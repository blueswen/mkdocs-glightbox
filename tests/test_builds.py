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


def validate_static(html_content: str, path: str = "", exist: bool = True):
    """
    Validate glightbox.min.css and glightbox.min.js have been loaded or not
    """
    assert exist == (
        re.search(
            rf'<link href="{re.escape(path)}assets\/stylesheets\/glightbox\.min\.css" rel="stylesheet"\/>',
            html_content,
        )
        is not None
    )
    assert exist == (
        re.search(
            rf'<script src="{re.escape(path)}assets\/javascripts\/glightbox\.min\.js"><\/script>',
            html_content,
        )
        is not None
    )


def validate_script(html_content: str, exist: bool = True):
    """
    Validate GLightbox have been initialized or not
    """
    assert exist == (
        re.search(
            r"const lightbox = GLightbox\((.*)\);",
            html_content,
        )
        is not None
    )


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
    contents = file.read_text(encoding="utf8")
    validate_static(contents)
    validate_script(contents)
    assert re.search(
        r'<a class="glightbox".*?href="img\.png".*?>\s*<img.*?src="img\.png".*?\/><\/a>',
        contents,
    )


def test_material(tmp_path):
    """
    Integrate with Material for MkDocs
    """
    mkdocs_file = "mkdocs-material.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/index.html"
    contents = file.read_text(encoding="utf8")
    validate_static(contents)
    validate_script(contents)
    assert re.search(
        r"document\$\.subscribe\(\(\) => { lightbox.reload\(\) }\);",
        contents,
    )
    assert re.search(
        r'<a class="glightbox".*?href="img\.png".*?>\s*<img.*?src="img\.png".*?\/><\/a>',
        contents,
    )


def test_material_instant(tmp_path):
    """
    Integrate with Material for MkDocs
    """
    mkdocs_file = "mkdocs-material-instant.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/index.html"
    contents = file.read_text(encoding="utf8")
    validate_static(contents)
    validate_script(contents)
    assert re.search(
        r"document\$\.subscribe\(\(\) => { lightbox.reload\(\) }\);",
        contents,
    )
    assert re.search(
        r'<a class="glightbox".*?href="img\.png".*?>\s*<img.*?src="img\.png".*?\/><\/a>',
        contents,
    )


def test_use_directory_urls(tmp_path):
    """
    Compatible with use_directory_urls is false or with --use-directory-urls and --use-directory-urls as args
    https://www.mkdocs.org/user-guide/configuration/#use_directory_urls
    https://www.mkdocs.org/user-guide/cli/
    """
    mkdocs_file = "mkdocs-target-file.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/sub_dir/page_in_sub_dir.html"
    contents = file.read_text(encoding="utf8")
    path = "../"
    validate_static(contents, path=path)
    validate_script(contents)
    assert re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}img\.png".*?>\s*<img.*?src="\.\.\/img\.png".*?\/><\/a>',
        contents,
    )


def test_disable_by_page(tmp_path):
    """
    Disable by page with page meta
    """
    mkdocs_file = "mkdocs.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/disable_by_page/index.html"
    contents = file.read_text(encoding="utf8")
    validate_static(contents, exist=False)
    validate_script(contents, exist=False)
    assert (
        re.search(
            r'<a class="glightbox".*?href="img\.png".*?>\s*<img.*?src="img\.png".*?\/><\/a>',
            contents,
        )
        is None
    )


def test_disable_by_image(tmp_path):
    """
    Disable by the image with image custom class or predefined class
    """
    mkdocs_file = "mkdocs-disable-by-image.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/disable_by_image/index.html"
    contents = file.read_text(encoding="utf8")
    path = "../"
    validate_static(contents, path=path)
    validate_script(contents)
    assert re.search(
        rf'<p><img.*?class="off-glb".*?src="{re.escape(path)}img\.png".*?\/><\/p>',
        contents,
    )
    assert re.search(
        rf'<p><img.*?class="skip-lightbox".*?src="{re.escape(path)}img\.png".*?\/><\/p>',
        contents,
    )
    assert re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}img\.png".*?><img.*?src="{re.escape(path)}img\.png".*?\/><\/a>',
        contents,
    )


@pytest.mark.parametrize("emoji_name", EMOJI_LIST)
def test_disable_with_emoji(emoji_name, tmp_path):
    """
    Disable when the image with emoji class name(defined in PyMdown Extensions): emojione, gemoji, twemoji
    https://facelessuser.github.io/pymdown-extensions/extensions/emoji/
    """
    mkdocs_file = f"mkdocs-material-{emoji_name}.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/emoji/index.html"
    contents = file.read_text(encoding="utf8")
    validate_static(contents, path="../")
    validate_script(contents)
    assert re.search(
        rf'<p><img.*?class="{re.escape(emoji_name)}".*?\/>.*?<\/p>',
        contents,
    )


def test_url(tmp_path):
    """
    Compatible with URL
    """
    mkdocs_file = "mkdocs.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/url/index.html"
    contents = file.read_text(encoding="utf8")
    validate_static(contents, path="../")
    validate_script(contents)
    image_url = re.escape("https://dummyimage.com/600x400/bdc3c7/fff.png")
    assert re.search(
        rf'<a class="glightbox".*?href="{image_url}".*?><img.*?src="{image_url}".*?\/><\/a>',
        contents,
    )


def test_default_options(tmp_path):
    """
    Validate GLightbox default options
    """
    mkdocs_file = "mkdocs.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/images/index.html"
    contents = file.read_text(encoding="utf8")
    path = "../"
    validate_static(contents, path)
    validate_script(contents)
    regex_obj = re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}img\.png.*?"><img.*?src="{re.escape(path)}img\.png".*?\/><\/a>',
        contents,
    )

    # validate position
    regex_obj = re.search(
        r"const lightbox = GLightbox\((.*)\);",
        contents,
    )
    assert regex_obj
    text = regex_obj.group(1)
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
        assert option in text


def test_options(tmp_path):
    """
    Validate GLightbox options setting through plugins
    """
    mkdocs_file = "mkdocs-options.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/images/index.html"
    contents = file.read_text(encoding="utf8")
    path = "../"
    validate_static(contents, path)
    validate_script(contents)
    # validate override style
    assert ".gslide-image img { background: none; }" in contents
    assert (
        """.glightbox-clean .gslide-media {
        -webkit-box-shadow: none;
        box-shadow: none;
    }"""
        in contents
    )
    # validate slide options
    regex_obj = re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}img\.png"(.*?)><img.*?src="{re.escape(path)}img\.png".*?\/><\/a>',
        contents,
    )
    assert regex_obj
    text = regex_obj.group(1)
    assert 'data-height="60%"' in text
    assert 'data-width="80%"' in text
    assert 'data-desc-position="right"' in text

    # validate GLightbox options
    regex_obj = re.search(
        r"const lightbox = GLightbox\((.*)\);",
        contents,
    )
    assert regex_obj
    text = regex_obj.group(1)
    options = [
        '"touchNavigation": false',
        '"loop": true',
        '"zoomable": false',
        '"draggable": false',
        '"openEffect": "fade"',
        '"closeEffect": "fade"',
        '"slideEffect": "fade"',
    ]
    for option in options:
        assert option in text


def test_gallery(tmp_path):
    """
    Validate gallery
    """
    mkdocs_file = "mkdocs-material.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/gallery/index.html"
    contents = file.read_text(encoding="utf8")
    path = "../"
    validate_static(contents, path=path)
    validate_script(contents)
    regex_obj = re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}img\.png"(.*?)><img alt="image-a".*?src="{re.escape(path)}img\.png".*?\/><\/a>',
        contents,
    )
    assert regex_obj
    text = regex_obj.group(1)
    assert 'data-gallery="1"' in text

    regex_obj = re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}img\.png"(.*?)><img alt="image-b".*?src="{re.escape(path)}img\.png".*?\/><\/a>',
        contents,
    )
    assert regex_obj
    text = regex_obj.group(1)
    assert 'data-gallery="1"' in text

    regex_obj = re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}another-img\.png"(.*?)><img alt="image-c".*?src="{re.escape(path)}another-img\.png".*?\/><\/a>',
        contents,
    )
    assert regex_obj
    text = regex_obj.group(1)
    assert 'data-gallery="2"' in text

    regex_obj = re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}another-img\.png"(.*?)><img alt="image-d".*?src="{re.escape(path)}another-img\.png".*?\/><\/a>',
        contents,
    )
    assert regex_obj
    text = regex_obj.group(1)
    assert 'data-gallery="2"' in text


def test_caption(tmp_path):
    """
    Validate captions feature
    """
    mkdocs_file = "mkdocs-material.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/caption/index.html"
    contents = file.read_text(encoding="utf8")
    path = "../"
    validate_static(contents, path=path)
    validate_script(contents)

    # validate title and description
    regex_obj = re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}img\.png"(.*?)><img alt="image-default".*?src="{re.escape(path)}img\.png".*?\/><\/a>',
        contents,
    )
    assert regex_obj
    text = regex_obj.group(1)
    assert 'data-description="data-description"' in text
    assert 'data-title="data-title"' in text

    # validate position
    regex_obj = re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}img\.png"(.*?)><img alt="image-right".*?src="{re.escape(path)}img\.png".*?\/><\/a>',
        contents,
    )
    assert regex_obj
    text = regex_obj.group(1)
    assert 'data-desc-position="right"' in text

    # validate compatible with figure
    regex_obj = re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}img\.png"(.*?)><img alt="image-figure".*?src="{re.escape(path)}img\.png".*?\/><\/a><\/p>',
        contents,
    )
    assert regex_obj
    text = regex_obj.group(1)
    assert 'data-description="data-description"' in text
    assert 'data-title="data-title"' in text


def test_auto_caption_by_page(tmp_path):
    """
    Validate auto captions with image tag alt by page
    """
    mkdocs_file = "mkdocs-material.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/auto_caption/index.html"
    contents = file.read_text(encoding="utf8")
    path = "../"
    validate_static(contents, path=path)
    validate_script(contents)
    # validate title and description
    regex_obj = re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}img\.png"(.*?)><img.*?src="{re.escape(path)}img\.png".*?\/><\/a>',
        contents,
    )
    assert regex_obj
    text = regex_obj.group(1)
    assert 'data-title="alt as caption"' in text


def test_auto_caption(tmp_path):
    """
    Validate auto captions with image tag alt for all page
    """
    mkdocs_file = "mkdocs-auto-caption.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/index.html"
    contents = file.read_text(encoding="utf8")
    validate_static(contents)
    validate_script(contents)
    regex_obj = re.search(
        r'<a class="glightbox".*?href="img\.png"(.*?)><img.*?src="img\.png".*?\/><\/a>',
        contents,
    )
    assert regex_obj
    text = regex_obj.group(1)
    assert 'data-title="image"' in text


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
    contents = file.read_text(encoding="utf8")
    validate_static(contents)
    validate_script(contents)
    assert re.search(
        r"document\$\.subscribe\(\(\) => { lightbox.reload\(\) }\);",
        contents,
    )
    assert re.search(
        r'<a class="glightbox".*?href="img\.png".*?>\s*<img.*?src="img\.png".*?\/><\/a>',
        contents,
    )


def test_site_url(tmp_path):
    """
    Compatible with the site with path prefix
    """
    mkdocs_file = "mkdocs-site-url.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/index.html"
    contents = file.read_text(encoding="utf8")
    validate_static(contents)
    validate_script(contents)
    assert re.search(
        r'<a class="glightbox".*?href="img\.png".*?>\s*<img.*?src="img\.png".*?\/><\/a>',
        contents,
    )

    file = testproject_path / "site/images/index.html"
    contents = file.read_text(encoding="utf8")
    path = "../"
    validate_static(contents, path)
    validate_script(contents)
    assert re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}img\.png".*?><img.*?src="{re.escape(path)}img\.png".*?\/><\/a>',
        contents,
    )


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
    contents = file.read_text(encoding="utf8")
    path = "../"
    validate_static(contents, path)
    validate_script(contents)
    assert (
        re.search(
            rf'<a class="glightbox".*?href="{re.escape(path)}img\.png".*?><img.*?src="{re.escape(path)}img\.png".*?\/><\/a>',
            contents,
        )
        is None
    )


def test_image_without_ext(tmp_path):
    """
    Image without extension
    """
    mkdocs_file = "mkdocs.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/without_ext/index.html"
    contents = file.read_text(encoding="utf8")
    path = "../"
    validate_static(contents, path)
    validate_script(contents)
    assert re.search(
        r'<a class="glightbox".*?href="https://picsum\.photos/1200/800".*?data-type="image".*?><img.*?src="https://picsum\.photos/1200/800".*?\/><\/a>',
        contents,
    )


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
    contents = file.read_text(encoding="utf8")
    validate_static(contents)
    validate_script(contents)


def test_privacy(tmp_path):
    """
    Compatible with material privacy plugin
    """
    mkdocs_file = "mkdocs-material-privacy.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/url/index.html"
    contents = file.read_text(encoding="utf8")
    validate_static(contents, path="../")
    validate_script(contents)
    image_url = re.escape("../assets/external/dummyimage.com/600x400/bdc3c7/fff.png")
    assert re.search(
        rf'<a class="glightbox"(?!.*href=).*?><img.*?src="{image_url}".*?><\/a>',
        contents,
    )
    patch_script = re.escape(
        "document.querySelectorAll('.glightbox').forEach(function(element) {"
    )
    assert re.search(
        rf"{patch_script}",
        contents,
    )


def test_enable_by_image(tmp_path):
    """
    Enable by the image with on-glb class
    """
    mkdocs_file = "mkdocs-material.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/enable_by_image/index.html"
    contents = file.read_text(encoding="utf8")
    path = "../"
    validate_static(contents, path=path)
    validate_script(contents)
    assert re.search(
        rf'<p><img alt="image" src="{re.escape(path)}img\.png" \/><\/p>',
        contents,
    )
    assert re.search(
        rf'<a class="glightbox".*?href="{re.escape(path)}img\.png".*?><img.*?class="on-glb".*?src="{re.escape(path)}img\.png".*?\/><\/a>',
        contents,
    )


def test_manual(tmp_path):
    """
    Manual mode
    """
    mkdocs_file = "mkdocs-manual.yml"
    testproject_path = validate_mkdocs_file(tmp_path, f"tests/fixtures/{mkdocs_file}")
    file = testproject_path / "site/index.html"
    contents = file.read_text(encoding="utf8")
    validate_static(contents)
    validate_script(contents)
    assert (
        re.search(
            r'<a class="glightbox".*?href="img\.png".*?>\s*<img.*?src="img\.png".*?\/><\/a>',
            contents,
        )
        is None
    )

    file = testproject_path / "site/manual/index.html"
    contents = file.read_text(encoding="utf8")
    validate_static(contents, path="../")
    validate_script(contents)
    assert re.search(
        r'<a class="glightbox".*?href="..\/img\.png".*?>\s*<img.*?src="..\/img\.png".*?\/><\/a>',
        contents,
    )

    file = testproject_path / "site/manual_enable_by_page/index.html"
    contents = file.read_text(encoding="utf8")
    validate_static(contents, path="../")
    validate_script(contents)
    assert re.search(
        r'<a class="glightbox".*?href="..\/img\.png".*?>\s*<img.*?alt="image-a" src="..\/img\.png".*?\/><\/a>',
        contents,
    )

    assert (
        re.search(
            r'<a class="glightbox".*?href="..\/img\.png".*?>\s*<img.*?alt="image-b" src="..\/img\.png".*?\/><\/a>',
            contents,
        )
        is None
    )

    assert re.search(
        r'<a class="glightbox".*?href="..\/img\.png".*?>\s*<img.*?alt="image-c" src="..\/img\.png".*?\/><\/a>',
        contents,
    )
