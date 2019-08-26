# Boorunaut
[![Build Status](https://travis-ci.com/Boorunaut/Boorunaut.svg?branch=master)](https://travis-ci.com/Boorunaut/Boorunaut)

![Welcome page screenshot of Boorunaut](assets/PostListingScreenshot.png)

Boorunaut is a taggable imageboard built in [Django](https://www.djangoproject.com). Based on [Danbooru](https://github.com/r888888888/danbooru).

It is able to be used locally to categorize images, or ready to configure and deploy as a website.

* [Source repository](https://github.com/Boorunaut/Boorunaut)
* [Documentation](https://boorunaut.gitbook.io/docs/)

## Features
* Posts;
* Gallery system;
* Tagging system, with aliases and implications;
* Control panel, including mass renaming, hash banning, mod queue and more.

## Installing

```
pip install Boorunaut
boorunaut startproject mysite
```

By default, the database is set to SQLite. For production, it is recommended to change it to another one, like PostgreSQL.
