from distutils.core import setup

setup(
    name="dutch_news_scrapers",
    version="0.6",
    description="Generic Dutch News Scrapers",
    author="Wouter van Atteveldt",
    author_email="wouter@vanatteveldt.com",
    packages=["dutch_news_scrapers"],
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing",
    ],
    install_requires=[
        "requests",
        "lxml",
        "cssselect",
        "amcat4apiclient",
        "nltk",
        "xmltodict",
        "fake_useragent"
    ]
)
