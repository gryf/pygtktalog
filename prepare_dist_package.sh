#!/bin/sh
# remove ~, pyc, pyo files from current directory

mkdir t 2>/dev/null
if [ $? != 0 ]; then
	echo "cannot create directory 't': File exist."
	echo "Rename it, move or rename, bcoz it's on the way."
	exit
fi
cd t
alias ls=ls

PREV=`ls -1 ..|grep bz2|tail -n 1|cut -f '2' -d '_'|cut -f 1 -d '.'`
REV=`svn export svn://10.0.0.10/repos/Python/pyGTKtalog pyGTKtalog |tail -n 1|cut -f 3 -d " "|cut -f 1 -d '.'`

cd pyGTKtalog
find . -name \*~ -exec rm '{}' ';'
find . -name \*pyc -exec rm '{}' ';'
find . -name \*pyo -exec rm '{}' ';'
find . -type d -name .svn -exec rm -fr '{}' ';'
rm -fr db img
rm -fr prepare_dist_package.sh

svn log -r ${PREV}:HEAD -v svn://10.0.0.10/repos/Python/pyGTKtalog > CHANGELOG

cd ..

tar jcf ../pygtktalog_${REV}.tar.bz2 pyGTKtalog

cd ..
rm -fr t

