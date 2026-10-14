# BluePrint: install the `blueprint` command, the prompts, and the tools.
#
#   make install            install into $(PREFIX) and install the Claude skills
#   make install SKILLS=0   install, but do not install the Claude skills
#   make link               link $(PREFIX)/bin/blueprint to this directory (for development)
#   make uninstall          remove the installed files and the Claude skills
#   make test               run the self-tests and the linters
#
# PREFIX is ~/.local by default. Make sure that $(PREFIX)/bin is on your PATH.

PREFIX  ?= $(HOME)/.local
BINDIR  := $(PREFIX)/bin
DATADIR := $(PREFIX)/share/blueprint
SKILLS  ?= 1
PYTHON  ?= python3

STE_SKILL := tools/asd-ste100-skill

.PHONY: all install link uninstall test submodules

all: test

submodules:
	@test -f $(STE_SKILL)/SKILL.md || git submodule update --init

install: submodules
	install -d $(BINDIR) $(DATADIR)/prompts $(DATADIR)/tools/ears-lint
	install -m 0755 bin/blueprint $(BINDIR)/blueprint
	install -m 0644 catalog.tsv README.md CHANGELOG.md LICENSE $(DATADIR)/
	install -m 0644 prompts/*.md $(DATADIR)/prompts/
	install -m 0755 tools/ears-lint/ears-lint.py $(DATADIR)/tools/ears-lint/
	rm -rf $(DATADIR)/$(STE_SKILL)
	mkdir -p $(DATADIR)/tools
	cp -R $(STE_SKILL) $(DATADIR)/$(STE_SKILL)
	rm -rf $(DATADIR)/$(STE_SKILL)/.git
	@if [ "$(SKILLS)" = "1" ]; then $(BINDIR)/blueprint install-skills; fi
	@echo "Installed. Run 'blueprint' to see the prompts and tools."

link: submodules
	install -d $(BINDIR)
	ln -sf $(CURDIR)/bin/blueprint $(BINDIR)/blueprint
	@if [ "$(SKILLS)" = "1" ]; then $(BINDIR)/blueprint install-skills; fi
	@echo "Linked. 'blueprint' now uses $(CURDIR)."

uninstall:
	-@test -x $(BINDIR)/blueprint && $(BINDIR)/blueprint uninstall-skills
	rm -f $(BINDIR)/blueprint
	rm -rf $(DATADIR)

test: submodules
	$(PYTHON) -I tools/ears-lint/ears-lint.py --selftest
	$(PYTHON) -I $(STE_SKILL)/scripts/ste-lint.py --selftest
	$(PYTHON) -I bin/blueprint list > /dev/null
