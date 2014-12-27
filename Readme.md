# Address Book Manager For Hagaki Sakka

## General

This is address book manager and csv file generator for [Hagaki Sakka](http://www.hagakisakka.jp/).  

Require Python 2.7 or Python 3.3 (depend of Flask)

## Install

get source from repository

    $ git clone git://github.com/higebobo/hagaki-sakka.git
    $ cd hagaki-sakka
    $ mkdir log
    $ mkdir data

## Run as web service

run server

    $ python app.py

run server (via GNU Make)

    $ make run

## Command line usage

import data from raw csv

    $ ./main.py -m import -y <year> (--init)

export data into csv for hagaki sakka importable

    $ ./main.py -m export -y <year>

add new year data

    $ ./main.py -m add -y <year>

## Release note

* 2014-06-11

    - First release
