include .env*

.PHONY: all clean FORCE pip test

all: $(ZTH_HTML_FILE)

$(ZTH_VERSION_FILE):
	echo 0 > $(ZTH_VERSION_FILE)

out:
	mkdir -p out

# always run
FORCE:

$(ZTH_JSON_FILE): FORCE out $(ZTH_VERSION_FILE)
	$(ZTH_PYTHON) ./download_bib.py --out=$@

$(ZTH_HTML_FILE): $(ZTH_JSON_FILE)
	cat $(ZTH_JSON_FILE) | $(ZTH_PYTHON) ./bib2html.py --out=$@
	# deploy it
	cp $(ZTH_HTML_FILE) $(ZTH_DEPLOY_TARGET)

test:
	$(ZTH_PYTHON) -m doctest download_bib.py

clean:
	rm -rf $(ZTH_OUT_DIR)

