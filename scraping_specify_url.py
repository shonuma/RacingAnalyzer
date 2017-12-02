# -*- coding: utf-8 -*-

import sys

from libs.scrape import Scrape

url = sys.argv[1]

scrape = Scrape()

if 'shutuba' in url:
    print(scrape.fetch_entry(url))
elif 'result' in url:
    print(scrape.fetch_result(url))
