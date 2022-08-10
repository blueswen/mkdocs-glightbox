# MkDocs GLightbox 

[![PyPI version](https://img.shields.io/pypi/v/mkdocs-glightbox.svg)](https://pypi.org/project/mkdocs-glightbox)
[![PyPI downloads](https://img.shields.io/pypi/dm/mkdocs-glightbox.svg)](https://pypi.org/project/mkdocs-glightbox)

A MkDocs plugin supports image lightbox with [GLightbox](https://github.com/biati-digital/glightbox).

GLightbox is a pure javascript lightbox library with mobile support.

[Live demo](https://blueswen.github.io/mkdocs-glightbox/) with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Dependency

1. Python Package
   1. beautifulsoup4>=4.11.1
2. GLightbox javascript file and css file
   1. GLightbox==3.2.0

## Usage

1. Install plugin from pypi

    ```bash
    pip install mkdocs-glightbox
    ```

2. Add ```glightbox``` plugin to your mkdocs.yml plugins sections:

    ```yaml
    plugins:
       - glightbox
    ```

3. You may customize the plugin by passing options in mkdocs.yml:

    ```yaml
    plugins:
       - glightbox:
           touchNavigation: true
           loop: false
           effect: zoom
           width: 100%
           height: auto
           zoomable: true
           draggable: true
    ```

    | Option          | Default | Description                                                                                                  |
    |-----------------|---------|--------------------------------------------------------------------------------------------------------------|
    | touchNavigation | true    | Enable or disable the touch navigation (swipe).                                                              |
    | loop            | false   | Loop slides on end.                                                                                          |
    | effect          | zoom    | Name of the effect on lightbox open. (zoom, fade, none)                                                      |
    | width           | 100%    | Default width for inline elements and iframes. You can use any unit for example 90% or 100vw for full width. |
    | height          | auto    | Default height for inline elements and iframes. You can use any unit for example 90%, 100vh or auto.         |
    | zoomable        | true    | Enable or disable zoomable images.                                                                           |
    | draggable       | true    | Enable or disable mouse drag to go prev and next slide.                                                      |

    Check more options information on [GLightbox Docs](https://github.com/biati-digital/glightbox#lightbox-options).

4. For more flexibility, you can disable lightbox by a [specific image](https://blueswen.github.io/mkdocs-glightbox/disable/image) or a [specific page](https://blueswen.github.io/mkdocs-glightbox/disable/page).

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/Blueswen/mkdocs-glightbox/blob/main/LICENSE) file for details.
