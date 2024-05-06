You can keep the whole site's images without lightbox effect but only enable lightbox effect on specific images or images on specific pages with the `manual` plugin option.

```yaml
plugins:
  - glightbox:
      manual: true # enable manual mode, all images will not be added to the lightbox effect
```

## Enable specific images

Enable lightbox effect on specific images by adding `on-glb` class to the image through markdown_extensions ```attr_list```. Enable ```attr_list``` via ```mkdocs.yml```:

```yaml
markdown_extensions:
  - attr_list
```

Check more details about ```attr_list``` on the [official document](https://python-markdown.github.io/extensions/attr_list/).

### Demo

Only images with ```on-glb``` class will be added to the lightbox effect. Other images on the site will not be added to the lightbox effect.

```yaml
# mkdocs.yml
markdown_extensions:
  - attr_list

plugins:
  - glightbox:
      manual: true
```

```markdown

![Lanyu, Taiwan](../images/gallery/blueswen-lanyu.jpeg){ .on-glb } 
Lanyu, Taiwan. Credit: Blueswen

![Hallstatt, Austria](../images/gallery/blueswen-hallstatt.jpeg){ .on-glb } 
Hallstatt, Austria. Credit: Blueswen

![Madeira, Portugal](../images/gallery/blueswen-madeira.jpeg)
Madeira, Portugal. Credit: Blueswen

```

<figure markdown>

![Lanyu, Taiwan](../images/gallery/blueswen-lanyu.jpeg)

<figcaption>Lanyu, Taiwan. Credit: Blueswen</figcaption>
</figure>

<figure markdown>

![Hallstatt, Austria](../images/gallery/blueswen-hallstatt.jpeg)

<figcaption>Hallstatt, Austria. Credit: Blueswen</figcaption>
</figure>

<figure markdown>

![Madeira, Portugal](../images/gallery/blueswen-madeira.jpeg){ .off-glb }

<figcaption>Madeira, Portugal. Credit: Blueswen</figcaption>
</figure>

## Enable specific pages

Enable lightbox effect on specific pages, add page metadata ```glightbox: true``` through markdown_extensions ```meta```. Enable ```meta``` via ```mkdocs.yml```:

```yaml
markdown_extensions:
  - meta
```

Check more details about ```meta``` on the [official document](https://python-markdown.github.io/extensions/meta_data/).

### Demo

Only pages with `glightbox: true` meta will be added to the lightbox effect. Other images on the site will not be added to the lightbox effect.

```yaml
# mkdocs.yml
markdown_extensions:
  - meta

plugins:
  - glightbox:
      manual: true
```

```markdown
---
glightbox: true
---

![Castelo de São Jorge, Lisbon, Portugal](../images/gallery/blueswen-lisbon.jpeg)
Cabo da Roca, Portugal. Credit: Blueswen

![Yosemite, USA.](../images/gallery/blueswen-yosemite.jpeg)
Yosemite, USA. Credit: Blueswen

```

<figure markdown>

![Castelo de São Jorge, Lisbon, Portugal](../images/gallery/blueswen-lisbon.jpeg)

<figcaption>Cabo da Roca, Portugal. Credit: Blueswen</figcaption>
</figure>

<figure markdown>

![Yosemite, USA.](../images/gallery/blueswen-yosemite.jpeg)

<figcaption>Yosemite, USA. Credit: Blueswen</figcaption>
</figure>
