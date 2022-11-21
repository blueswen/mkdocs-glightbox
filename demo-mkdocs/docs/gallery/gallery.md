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
