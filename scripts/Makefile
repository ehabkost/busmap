all: hor-linhas.txt all-hor-html all-hor-txt

hor/%.html:
	cod=`basename $@ .html`; \
	python hor-get-html.py $$cod > $@

hor/%.txt: hor/%.html
	python hor-html2txt.py < $< > $@

do-all-hor-html: $(patsubst %,hor/%.html,$(LINES))
do-all-hor-txt: $(patsubst %,hor/%.txt,$(LINES))

all-hor-html: hor-linhas.txt
	l=$$(echo $$(cut -f1 hor-linhas.txt)); \
	$(MAKE) do-all-hor-html LINES="$$l"

all-hor-txt: hor-linhas.txt
	l=$$(echo $$(cut -f1 hor-linhas.txt)); \
	$(MAKE) do-all-hor-txt LINES="$$l"

hor-linhas.txt:
	python hor-ls-linhas.py > hor-linhas.txt
