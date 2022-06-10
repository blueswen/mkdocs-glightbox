# MkDocs GLightbox 

A MkDocs plugin supports image lightbox with [GLightbox](https://github.com/biati-digital/glightbox).

GLightbox is pure Javascript lightbox library with mobile support.

[Live demo](https://blueswen.github.io/mkdocs-glightbox/) with [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) theme.

## Dependency

1. Python Package
   1. beautifulsoup4==4.11.1
2. GLightbox javascript file and css file
   1. GLightbox==3.2.0

## Usage

1. Install plugin from pypi

    ```bash
    pip install mkdocs-glightbox
    ```

2. Add ```glightbox``` plugin in to your mkdocs.yml plugins sections:

    ```yaml
    plugins:
    - glightbox
    ```

3. You may customize the plugin by passing options in mkdocs.yml:

    ```yaml
    plugins:
    - glightbox:
        touchNavigation: false
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
    | loop            | true    | Loop slides on end.                                                                                          |
    | effect          | zoom    | Name of the effect on lightbox open. (zoom, fade, none)                                                      |
    | width           | 100%    | Default width for inline elements and iframes. You can use any unit for example 90% or 100vw for full width. |
    | height          | auto    | Default height for inline elements and iframes. You can use any unit for example 90%, 100vh or auto.         |
    | zoomable        | True    | Enable or disable zoomable images.                                                                           |
    | draggable       | True    | Enable or disable mouse drag to go prev and next slide.                                                      |

    Check more options information on [GLightbox Docs](https://github.com/biati-digital/glightbox#lightbox-options).

## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/Blueswen/mkdocs-glightbox/blob/main/LICENSE) file for details.
