You can disable lightbox of images separately by adding ```off-glb``` or customized class through markdown_extensions ```attr_list```. Enable ```attr_list``` via ```mkdocs.yml```:

```yaml
markdown_extensions:
  - attr_list
```

Check more details about ```attr_list``` on the [official document](https://python-markdown.github.io/extensions/attr_list/).

The customized classes could be set in plugin option:

```yaml
plugins:
  - glightbox:
      skip_classes:
        - skip-lightbox
```

## Demo

The lightbox of the image with class ```off-glb``` or ```skip-lightbox``` (a custom class in plugin ```skip_classes``` options) is disabled.

```markdown
![Lanyu, Taiwan](../images/gallery/blueswen-lanyu.jpeg){ .off-glb }

![Hallstatt, Austria](../images/gallery/blueswen-hallstatt.jpeg){ .skip-lightbox }

![Obertraun, Austria](../images/gallery/blueswen-obertraun.jpeg)
```

<figure markdown>

![Lanyu, Taiwan](../images/gallery/blueswen-lanyu.jpeg){ .off-glb }

<figcaption>Lanyu, Taiwan. Credit: Blueswen</figcaption>
</figure>

<figure markdown>

![Hallstatt, Austria](../images/gallery/blueswen-hallstatt.jpeg){ .skip-lightbox }

<figcaption>Hallstatt, Austria. Credit: Blueswen</figcaption>
</figure>

<figure markdown>

![Obertraun, Austria](../images/gallery/blueswen-obertraun.jpeg)

<figcaption>Obertraun, Austria. Credit: Blueswen</figcaption>
</figure>
