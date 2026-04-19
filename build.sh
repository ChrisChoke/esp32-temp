#!/usr/bin/sh


[ ! -d ./dist ] && mkdir -p dist/lib dist/templates

SRC_DIR=./src
DST_DIR=./dist

compile ()
(
    cp -r $SRC_DIR/* $DST_DIR
    for FILE in $(find $DST_DIR -type f ! -name "main.py" -name "*.py"); do mpy-cross $FILE; done
    find $DST_DIR -type f ! -name "main.py" -name "*.py" -exec rm {} \;
)

compile