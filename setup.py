import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

with io.open(os.path.join(BASE_DIR, 'requirements.txt'), encoding='utf-8') as fh:
    REQUIREMENTS = fh.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='Boorunaut',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A taggable imagebord built in Django.',
    long_description=README,
    url='https://github.com/Boorunaut/Boorunaut',
    author='Luk3M, NogardRyuu',
    author_email='luk3@hotmail.com.br, thiago_dragon_@hotmail.com',
    entry_points="""
    [console_scripts]
    boorunaut=booru.setup.start-project:main
    """,
    test_suite="runtests.start",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=REQUIREMENTS,
)