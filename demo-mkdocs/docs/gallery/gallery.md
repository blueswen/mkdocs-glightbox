# Gallery

Built-in GLightbox gallery feature can be used by adding attribute ```data-gallery``` through markdown_extensions ```attr_list```. The image with the same gallery name will be grouped as a galley in the light box. Enable ```attr_list``` via ```mkdocs.yml```:

```yaml
markdown_extensions:
  - attr_list
```

Check more details about ```attr_list``` on the [official document](https://python-markdown.github.io/extensions/attr_list/).

## Demo

There are two galleries: taipei and seattle.

```markdown title="Setting gallery with data-gallery attribute"
### Taipei

![Taipei, Taiwan. Credit: Yuyu Liu](yuyu-taipei-city.jpeg){data-gallery="taipei"}

![Taipei, Taiwan. Credit: Yuyu Liu](yuyu-taipei-sky.jpeg){data-gallery="taipei"}

### Seattle

![Seattle, America. Credit: Yuyu Liu](yuyu-seattle-1.jpeg){data-gallery="seattle"}

![Seattle, America. Credit: Yuyu Liu](yuyu-seattle-2.jpeg){data-gallery="seattle"}

![Seattle, America. Credit: Yuyu Liu](yuyu-seattle-3.jpeg){data-gallery="seattle"}
```

### Taipei

<figure markdown>

![Taipei, Taiwan. Credit: Yuyu Liu](yuyu-taipei-city.jpeg){data-gallery="taipei"}

<figcaption>Taipei, Taiwan. Credit: Yuyu Liu</figcaption>
</figure>

<figure markdown>

![Taipei, Taiwan. Credit: Yuyu Liu](yuyu-taipei-sky.jpeg){data-gallery="taipei"}

<figcaption>Taipei, Taiwan. Credit: Yuyu Liu</figcaption>
</figure>

### Seattle

<figure markdown>

![Seattle, America. Credit: Yuyu Liu](yuyu-seattle-1.jpeg){data-gallery="seattle"}

<figcaption>Seattle, America. Credit: Yuyu Liu</figcaption>
</figure>

<figure markdown>

![Seattle, America. Credit: Yuyu Liu](yuyu-seattle-2.jpeg){data-gallery="seattle"}

<figcaption>Seattle, America. Credit: Yuyu Liu</figcaption>
</figure>

<figure markdown>

![Seattle, America. Credit: Yuyu Liu](yuyu-seattle-3.jpeg){data-gallery="seattle"}

<figcaption>Seattle, America. Credit: Yuyu Liu</figcaption>
</figure>

## Dark and light mode

If you are using the mkdocs theme is material, then we provide an option `auto_themed` to enable the dark and light mode of the material theme. When enabled, the image with the same theme will be grouped as a galley in the light box.

Enabled in a similar way to option [`auto_caption`](../caption/caption.md#image-alt-as-the-caption).

Check more details about the dark and light mode on the [official document](https://squidfunk.github.io/mkdocs-material/reference/images/#light-and-dark-mode).
