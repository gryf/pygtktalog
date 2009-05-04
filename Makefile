PYTHON_EXEC = PYTHONPATH=/home/gryf/Devel/Python/pyGTKtalog:/home/gryf/.python_lib python
LOCALE = LC_ALL=pl_PL.utf8
FILE = pygtktalog.py
DIST = bin/prepare_dist_package.sh
POT_GEN = bin/generate_pot.py

.PHONY: run
run:
	@$(PYTHON_EXEC) $(FILE)

.PHONY: runpl
runpl:
	@export $(LOCALE) && $(PYTHON_EXEC) $(FILE)

.PHONY: clean
clean:
	@find . -name \*~ -exec rm '{}' ';'
	@find . -name \*pyc -exec rm '{}' ';'
	@find . -name \*pyo -exec rm '{}' ';'
	@echo "cleaned."

.PHONY: distclean
distclean: clean
	@rm -fr locale/*
	@echo "all cleaned up"

.PHONY: pot
pot:
	@if [ ! -d locale ]; then mkdir locale; fi
	@python $(POT_GEN) pygtktalog pygtktalog > locale/pygtktalog.pot
	@echo "locale/pygtktalog.pot (re)generated."

.PHONY: pltrans
pltrans: pot
	@if [ -f locale/pl.po ]; then \
		echo "Merging existing *.po file with regenerated *.pot"; \
		msgmerge -U locale/pl.po locale/pygtktalog.pot; \
	else \
		echo "Creating fresh *.po file"; \
		cp locale/pygtktalog.pot locale/pl.po; \
	fi;
	@$$EDITOR locale/pl.po
	@if [ ! -d locale/pl/LC_MESSAGES ]; then mkdir -p locale/pl/LC_MESSAGES; fi
	@echo "Compile message catalog for pl_PL.utf8"
	@msgfmt locale/pl.po -o locale/pl/LC_MESSAGES/pygtktalog.mo
	@echo "Message catalog for pl_PL.utf8 saved in locale/pl/LC_MESSAGES/pygtktalog.mo"

.PHONY: plgen
plgen: pot
	@echo "Compile message catalog for pl_PL.utf8"
	@msgfmt locale/pl.po -o locale/pl/LC_MESSAGES/pygtktalog.mo
	@echo "Message catalog for pl_PL.utf8 saved in locale/pl/LC_MESSAGES/pygtktalog.mo"

.PHONY: test
test:
	cd test && $(PYTHON_EXEC) run_tests.py

.PHONY: dist
dist:
	@$(DIST)

.PHONY: help
help:
	@echo "Possible commands for make are:"
	@echo
	@echo " run:        Run pyGTKtalog. Default."
	@echo " runpl:      Run pyGTKtalog with LC_ALL set to pl_PL.utf8."
	@echo " clean:      Remove .pyc, .pyo and .~ files."
	@echo " distclean:  As above, also removes generated locale files."
	@echo " pot:        Generate .pot file from sources and .glade files."
	@echo " pltrans:    Generate/merge polish translation file and then invoke editor."
	@echo "             Environment variable EDITOR is expected"
	@echo " plgen:      Just generate polish translation file without merging and"
	@echo "             editing."
	@echo " test:       Launch unit tests for application."
	@echo " dist:       Make distribution package."
	@echo
