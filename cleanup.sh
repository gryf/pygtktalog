#!/bin/sh
# remove ~, pyc, pyo files from current directory
find . -name \*~ -exec rm '{}' ';'
find . -name \*pyc -exec rm '{}' ';'
find . -name \*pyo -exec rm '{}' ';'
