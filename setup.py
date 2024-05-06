from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mkdocs-glightbox",
    version="0.4.0",
    author="Blueswen",
    author_email="blueswen.tw@gmail.com",
    url="https://blueswen.github.io/mkdocs-glightbox",
    project_urls={
        "Source": "https://github.com/Blueswen/mkdocs-glightbox",
    },
    keywords=["mkdocs", "plugin", "lightbox"],
    packages=find_packages(),
    license="MIT",
    description="MkDocs plugin supports image lightbox with GLightbox.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    entry_points={
        "mkdocs.plugins": [
            "glightbox = mkdocs_glightbox.plugin:LightboxPlugin",
        ]
    },
)
