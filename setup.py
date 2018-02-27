#!/usr/bin/env python

from setuptools import setup


setup(
    name='yatank-sputnikonline',
    version='0.0.15.2',
    description='Yandex.Tank SputnikOnline plugin',
    author='Ilya Krylov',
    author_email='ilya.krylov@gmail.com',
    url='http://github.com/sputnik-load/yatank-sputnikonline',
    packages=['yatank_SputnikOnline'],
    package_data={'yatank_SputnikOnline': ['templates/*',
                                           'static/favicon.ico',
                                           'static/css/*',
                                           'static/js/*.js',
                                           'static/js/*.coffee',
                                           'static/js/vendor/*.js',
                                           'static/fonts/*']},
    install_requires=[]
)
