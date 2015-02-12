#!/usr/bin/env python
# -*- coding: utf-8 -*-

# global imports
import argparse
import json
from pyquery import PyQuery
import pystache
import re
import sys

# local imports
import env
import log

logger = log.get()
args = None
renderer = pystache.Renderer(file_encoding='utf-8')
HYPERLINK_REGEX = re.compile(r"(https?://[^ ]+)")


def get_clean_bib(bib):
    """extract the html citation, remove the html boilerplate that zotero returns"""
    d = PyQuery(bib)
    return d('div.csl-right-inline').html()


def get_clean_zotero_link(links):
    """the default zotero link doesn't show an edit button.  fix that."""
    link = "https://www.zotero.org/groups/grouplens"
    if "alternate" in links:
        link = links["alternate"]["href"].replace('items', 'items/itemKey')
    return link


def hyperlink_string(s):
    """take a string, insert <a> tags where http://... is found"""
    # from http://stackoverflow.com/a/720137/293087
    return HYPERLINK_REGEX.sub(r'<a href="\1">\1</a>', s)


def split_text_to_list(s):
    """turn a string into a list of strings, using line-breaks as the splitter"""
    return [line for line in s.split('\n') if line]


def emit_html(zotero_json):
    current_year = 0
    for item in zotero_json:
        # emit a year template when we encounter a new one
        year = int(item['meta']['parsedDate'][:4]) if 'parsedDate' in item['meta'] else 'Unknown Publication Date'
        if year and year != current_year:
            current_year = year
            yield renderer.render_path('tmpl/year.mustache.html', {'year': year})

        # emit entry template
        yield renderer.render_path('tmpl/entry.mustache.html', item)


def main():
    logger.info("starting")
    zotero_json_str = sys.stdin.read()
    zotero_json = json.loads(zotero_json_str)

    for item in zotero_json:
        item['bibclean'] = get_clean_bib(item['bib'])

        # links
        note = item['csljson']['note'] if 'note' in item['csljson'] else ''
        item['more'] = split_text_to_list(note)
        if 'URL' in item['csljson']:
            item['more'].append(item['csljson']['URL'])
        item['more'].append("zotero: " + get_clean_zotero_link(item['links']))

        # add hyperlinks
        item['more'] = [hyperlink_string(s) for s in item['more']]

    with open(args.outfile, "w") as out:
        for html_fragment in emit_html(zotero_json):
            out.write(html_fragment.encode('utf-8'))

        css = renderer.render_path('tmpl/bib.mustache.css')
        js = renderer.render_path('tmpl/bib.mustache.js')
        scripts = renderer.render_path('tmpl/footer.mustache.html', {'js': js, 'css': css})
        out.write(scripts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='zotero json => html for grouplens.org')
    parser.add_argument('-o', '--out', dest='outfile', help='output file name')
    args = parser.parse_args()

    # validate args
    if not args.outfile:
        raise ValueError("Requires -o to run.")

    main()
