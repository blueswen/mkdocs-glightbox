---
glightbox: false
---

You can disable lightbox of all images on a specific page by adding page metadata ```glightbox: false``` through markdown_extensions ```meta```. Enable ```meta``` via ```mkdocs.yml```:

```yaml
markdown_extensions:
  - meta
```

Check more detail about ```meta``` on the [official document](https://python-markdown.github.io/extensions/meta_data/).

## Demo

All images' lightbox are disabled on this page.

```markdown
---
glightbox: false
---

![Lanyu, Taiwan](../images/gallery/blueswen-lanyu.jpeg) 
Lanyu, Taiwan. Credit: Blueswen

![Obertraun, Austria](../images/gallery/blueswen-obertraun.jpeg) 
Obertraun, Austria. Credit: Blueswen
```

![Lanyu, Taiwan](../images/gallery/blueswen-lanyu.jpeg) 
Lanyu, Taiwan. Credit: Blueswen

![Obertraun, Austria](../images/gallery/blueswen-obertraun.jpeg) 
Obertraun, Austria. Credit: Blueswen
