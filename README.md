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

## Installation

If you are on a Linux-based system, you can simply run `INSTALL.sh` to automatically setup everything on a virtual environment locally.

You can also check the documentation below for more detailed instructions on how to install the library and its requirements manually and on different systems.

### Python

The project is mainly written in the Python programming language, so it's an essential requirement. In order to download it, you can visit [the official website](https://www.python.org/), download it and install it.

On Linux you can just run the following command on the bash:

```bash
sudo apt-get install python3
```

Please check if `pip` was installed along it with the command:

```bash
python3 -m pip --version
```

If no errors occurred, then you are good.

### Virtual Environment

Now you need to have the python virtual environment installed on python in order to be able to create isolated local version of python on the desired directory. You just run the following on the bash:

```bash
python3 -m pip install virtualenv
```

#### Create the virtual environment

Now you create a new virtual environment on the directory you your choosing. After nativating to the directory, let's say it's called `mynewbooru` for example. Inside it, you can run on bash:

```bash
virtualenv env
```

This command will create a new virtual environment called `env`.
You need now to activate the environment before running any of the following commands (you also need to activate it every time you want to run the project, or else an error saying you don't have the libraries installed will occur).

On Linux you run:

```bash
source env/bin/activate
```

On Windows you run:

```bash
.\env\Scripts\activate
```

Now the environment is activated, so you are running an local isolated version of python. Anything you install here will not affect the "global" python installed on your system.

### Boorunaut

Finally, you can now install `Boorunaut` on your python environment:

```bash
pip install Boorunaut
```

And you can start a new your project with the command:

```bash
boorunaut startproject mysite
```

It will create a new project folder. You can enter it and run Django's (the underling tecnology behind Boorunaut) commands to initialize the website configuration. To enter the folder you can run:

```bash
cd mysite
```

Your project should have the following file structure:

```bash
mynewbooru/
├── env/
└── mysite/
    └── mysite
        ├── __init__.py
        └── ...
    ├── __init__.py
    └── manage.py
```

Then you run the following commands:


```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Now your website should be running on the default `localhost:8000`. Type that into your browser and check it out your own Boorunaut main page!

By default, the database is set to SQLite. For production, it is recommended to change it to another one, like PostgreSQL.
