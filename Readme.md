# Address Book Manager For Hagaki Sakka

## Overview

This is address book manager and csv file generator for [Hagaki Sakka](http://www.hagakisakka.jp/).

Now also available netprint csv format.

Require Python >= 2.7 or Python >= 3.3 (depend of Flask)

## Install

get source from the repository

    $ git clone git://github.com/higebobo/hagaki-sakka.git
    $ cd hagaki-sakka
    $ mkdir log
    $ mkdir data

## Run as web service

run server

    $ python manage.py runserver

run server (via GNU Make)

    $ make run

## Release note

* 2017-12-06
    - Use cdn service instead of static css and javascript file
* 2017-11-26
    - Add download for netprint csv format
* 2016-12-07
    - Bug fix for Python3
* 2015-12-12
    - Add year form
* 2015-10-19
    - Update to use class based view and so on
* 2014-12-27
    - Make repository in github.com
* 2014-06-11
    - First release

