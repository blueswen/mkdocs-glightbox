You can disable lightbox of images separately by adding ```off-glb``` class through markdown_extensions ```attr_list```. Enable ```attr_list``` via ```mkdocs.yml```:

```yaml
markdown_extensions:
  - attr_list
```

Check more detail about ```attr_list``` on the [official document](https://python-markdown.github.io/extensions/attr_list/).

## Demo

The first image's lightbox is disabled.

```markdown
![Lanyu, Taiwan](../images/gallery/blueswen-lanyu.jpeg){ .off-glb }
Lanyu, Taiwan. Credit: Blueswen

![Obertraun, Austria](../images/gallery/blueswen-obertraun.jpeg) 
Obertraun, Austria. Credit: Blueswen
```

![Lanyu, Taiwan](../images/gallery/blueswen-lanyu.jpeg){ .off-glb }
Lanyu, Taiwan. Credit: Blueswen

![Obertraun, Austria](../images/gallery/blueswen-obertraun.jpeg) 
Obertraun, Austria. Credit: Blueswen
