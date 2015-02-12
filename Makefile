include .env
include .env.local

.PHONY: all clean FORCE pip test formatonly deploy

all: out/grouplens-bib.html

$(VERSION_FILE):
	echo 0 > $(VERSION_FILE)

out:
	mkdir -p out

# always run
FORCE:

out/grouplens-bib.json: FORCE out $(VERSION_FILE)
	./download_bib.py --out=$@

out/grouplens-bib.html: out/grouplens-bib.json
	cat out/grouplens-bib.json | ./bib2html.py --out=$@
	# deploy it
	cp out/grouplens-bib.html ../../wp-content/themes/roots/templates/gl-publications-generated.php

test:
	python -m doctest download_bib.py

pip:
	pip install -r requirements.txt

clean:
	rm -rf out


# development tasks

# skip the download step
formatonly:
	cat out/grouplens-bib.json | ./bib2html.py --out=out/grouplens-bib.html

deploy:
	scp out/grouplens-bib.html presspot.cs.umn.edu:/export/scratch/grplens/grplens-wordpress/wp-content/themes/roots/templates/gl-publications-generated.php

