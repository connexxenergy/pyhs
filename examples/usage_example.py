#!/usr/bin/env python
"""Simple usage example.

usage:
./usage_example.py url id password
e.g.:
./usage_example.py http://localhost/test-project/haystack scott@example.com tiger

"""
import sys
from hs.client import HClient
from hs.io import ZincWriter
from pprint import pprint

def start_nav(client):
    """Browse the site using haystack nav command"""
    res = client.nav()
    if res.rows:
        for row in res.rows:
            do_nav(client, row, 0)

def start_example(client):
    """Run example commands/functions.
    >>> client = HClient("http://cd.example.com/demo", "scott@example.com", "tiger")
    >>> start_example(client)
    """
    client.about()
    res = client.about()
    pprint(dict(res))
    #print('level=%d'%level)
    client.contentType = 'zinc'
    grid = client.about()
    print(ZincWriter.gridToString(grid))


    
def main(argv=None):
    client = HClient(argv[1], argv[2], argv[3])
    #res = client.about()    
    start_example(client)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    

