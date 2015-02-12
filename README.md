# zotero-to-html

turn a zotero collection into an html page

This code first downloads a bibliography using uses the
[Zotero API](https://www.zotero.org/support/dev/web_api/v3/basics),
then parses that bibliography into html for display on the web.  It asks Zotero politely
whether the bibliography has changed since the last run, to keep things lightweight unless things have changed.
However, this process will rebuild the entire bibliography from scratch each time the version changes, so it may not
scale to extremely large bibliographies, especially those that are changed often.


# requirements

* python 2.7.x (not tested on python 3)
* gnu make
* zotero API key (create one at https://www.zotero.org/settings/keys)


# install + configure

You probably should use a virtualenv, then:

    pip install -r requirements.txt

Edit `.env` directly or create `.env.local` to override the settings.  In particular, you will need to override the
zotero api key, the zotero search parameters, and the output paths.

If you're querying a group, you can find its id by visiting a url like this:

    https://api.zotero.org/users/1800868/groups?v=3&key=FOOFOOFOO

If you want to write your own templates, copy the tmpl directory somewhere, edit the files, and change `ZTH_TMPL_DIR`


# run

    make

Probably, you'll want to run `make` in a cron job to keep the output up to date.

If you need to change the settings and re-run:

    make clean
    make
