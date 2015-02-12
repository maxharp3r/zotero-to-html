include .env
include .env.local

.PHONY: all clean FORCE pip test formatonly deploy

all: $(ZTH_HTML_FILE)

$(ZTH_VERSION_FILE):
	echo 0 > $(ZTH_VERSION_FILE)

out:
	mkdir -p out

# always run
FORCE:

$(ZTH_JSON_FILE): FORCE out $(ZTH_VERSION_FILE)
	./download_bib.py --out=$@

$(ZTH_HTML_FILE): $(ZTH_JSON_FILE)
	cat $(ZTH_JSON_FILE) | ./bib2html.py --out=$@
	# deploy it
	cp $(ZTH_HTML_FILE) $(ZTH_DEPLOY_TARGET)

test:
	python -m doctest download_bib.py

pip:
	pip install -r requirements.txt

clean:
	rm -rf $(ZTH_OUT_DIR)


# development tasks

# skip the download step
formatonly:
	cat out/grouplens-bib.json | ./bib2html.py --out=out/grouplens-bib.html

deploy:
	scp out/grouplens-bib.html presspot.cs.umn.edu:/export/scratch/grplens/grplens-wordpress/wp-content/themes/roots/templates/gl-publications-generated.php

