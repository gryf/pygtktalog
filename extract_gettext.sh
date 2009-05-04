#!/bin/sh
# Create new messages.pot file
blacklist="EXIF.py no_thumb.py"
rm locale/pygtktalog.pot
xgettext -L Python --keyword=_ -o locale/pygtktalog.pot pygtktalog.py

svn ls | grep '.py$'|grep -v 'pygtktalog.py' |while read file; do
    xgettext -j -L Python --keyword=_ -o locale/pygtktalog.pot $file
done

for dir in src/ctrls src/models src/views src/lib; do
	svn ls -R $dir| grep '.py$' |grep -v 'EXIF.py'|grep -v 'no_thumb.py'| while read file; do
		xgettext -j -L Python --keyword=_ -o locale/pygtktalog.pot $dir/$file
	done
done

cd locale
msginit --input=pygtktalog.pot --locale=pl_PL.UTF-8

# now its time to make .mo files:
mkdir -p pl_PL/LC_MESSAGES
#msgfmt --output-file=pl_PL/LC_MESSAGES/pygtktalog.mo pl.po

