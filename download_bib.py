#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Download the grouplens bibliography from zotero, write the output to a file.

Zotero has a way of checking if things have changed, which we use. If the bibliography has not changed, then
we do not write anything to the file.

Docs:
* https://www.zotero.org/support/dev/web_api/v3/basics
* https://www.zotero.org/styles/
* https://www.zotero.org/settings/keys
* https://github.com/brechtm/citeproc-py
"""

import argparse
import json
import os
import re
import requests

# local imports
import env

logger = env.logger()

REL_NEXT_REGEX = re.compile(r'rel="next"')
LINK_START_REGEX = re.compile(r"start=(\d+)")

new_version = None


def _write_current_version(version_id):
    with open(os.getenv("ZTH_VERSION_FILE"), "w") as version_file:
        version_file.write(str(version_id))


def _read_current_version():
    ver = 0
    try:
        with open(os.getenv("ZTH_VERSION_FILE"), "r") as version_file:
            ver = int(version_file.read())
    except IOError:
        pass
    return ver


def _get_next_start(links_header):
    """parse the zotero `Link` header into a new start value, or None if we're done.

    >>> link = '<https://api.zotero.org/groups/14159/items?include=bib%2Ccsljson&limit=100&sort=date&start=100&style=acm-sigchi-proceedings&v=3>; rel="next", <https://api.zotero.org/groups/14159/items?include=bib%2Ccsljson&limit=100&sort=date&start=400&style=acm-sigchi-proceedings&v=3>; rel="last", <https://www.zotero.org/groups/14159/items>; rel="alternate"'
    >>> _get_next_start(link)
    100
    >>> link_without_next = '<https://api.zotero.org/groups/14159/items?include=bib%2Ccsljson&limit=100&sort=date&style=acm-sigchi-proceedings&v=3>; rel="first", <https://www.zotero.org/groups/14159/items>; rel="alternate"'
    >>> _get_next_start(link_without_next) is None
    True
    >>> link_full = '<https://api.zotero.org/groups/14159/items?include=bib%2Ccsljson&limit=100&sort=date&style=acm-sigchi-proceedings&tag=grouplens.org>; rel="first", <https://api.zotero.org/groups/14159/items?include=bib%2Ccsljson&limit=100&sort=date&start=100&style=acm-sigchi-proceedings&tag=grouplens.org>; rel="prev", <https://api.zotero.org/groups/14159/items?include=bib%2Ccsljson&limit=100&sort=date&start=300&style=acm-sigchi-proceedings&tag=grouplens.org>; rel="next", <https://api.zotero.org/groups/14159/items?include=bib%2Ccsljson&limit=100&sort=date&start=300&style=acm-sigchi-proceedings&tag=grouplens.org>; rel="last", <https://www.zotero.org/groups/14159/items>; rel="alternate"'
    >>> _get_next_start(link_full)
    300
    """
    if links_header is not None:
        parts = links_header.split(', ')
        for part in parts:
            if REL_NEXT_REGEX.search(part):
                match = LINK_START_REGEX.search(part)
                if match and len(match.groups()) == 1:
                    return int(match.groups()[0])
    return None


def get_bib_from_zotero(min_version=0, offset=0):
    """fetch bibliography as csljson, returns the next offset or None if we're done"""
    global new_version
    url = "https://api.zotero.org/%s/items" % os.environ["ZTH_SEARCH_PREFIX_URI"]
    url_params = {
        "sort": "date",
        "tag": os.getenv("ZTH_SEARCH_TAG"),
        "format": "json",
        "include": "bib,csljson",
        "style": os.getenv("ZTH_CITEPROC_STYLE"),
        "start": offset,
        "limit": 100
    }
    url_headers = {
        "Zotero-API-Version": 3,
        "Authorization": "Bearer %s" % os.getenv("ZTH_API_KEY"),
        "If-Modified-Since-Version": str(min_version)
    }
    r = requests.get(url, params=url_params, headers=url_headers)

    if r.status_code == 304:
        # bibliography has not changed
        logger.info("no change. current version: %d" % min_version)
        next_start = None
        parsed_response = None
    elif r.status_code == 200:
        if offset == 0:
            new_version = r.headers["Last-Modified-Version"]
            logger.info("downloading new version of bibliography. new version: %s" % new_version)
        next_start = _get_next_start(r.headers["Link"])
        parsed_response = r.json()
    else:
        logger.error("error: %s" % r.status_code)
        exit(1)

    return next_start, parsed_response


def main():
    parser = argparse.ArgumentParser(description="download bibliography from zotero into citeproc_json file.")
    parser.add_argument("-o", "--out", dest="outfile", help="output file name")
    args = parser.parse_args()

    # validate args
    if not args.outfile:
        raise ValueError("Requires -o to run.")

    logger.info("starting")
    min_version = _read_current_version()

    # zotero limits us to query one page at a time when we include the "bib" format
    offset = 0
    bib_entries_from_zotero = []
    while offset is not None:
        offset_new, parsed_response = get_bib_from_zotero(min_version, offset)
        if offset_new and offset_new <= offset:
            raise Exception("going backwards!")
        else:
            offset = offset_new
        if parsed_response:
            bib_entries_from_zotero.extend(parsed_response)

    if len(bib_entries_from_zotero) > 0:
        with open(args.outfile, "w") as out:
            json.dump(bib_entries_from_zotero, out, indent=2)

    # write the new version number as the last step (only increment in the absence of failures)
    if new_version is not None:
        _write_current_version(new_version)

    exit(0)


if __name__ == "__main__":
    main()
