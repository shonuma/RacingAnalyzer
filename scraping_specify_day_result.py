# -*- coding: utf-8 -*-

import os
import sys
from argparse import ArgumentParser

from libs.scrape import Scrape

usage = """
引数に競馬場、開催、日数のリスト(05:05:01, 09:05:01, 07:04:01)を指定する
- 中山(05) 5回(05) 1日目(01)
- 阪神(09) 5回(09) 1日目(01)
- 中京(07) 4回(04) 1日目(01)

python {} -l 05:05:01,09:05:01,07:04:01
# 出馬表は取得しない
"""[1:-1].format(os.path.basename(__file__))

argparser = ArgumentParser(usage=usage)
argparser.add_argument('--list', '-l', type=str, help='set placeinfo.')
argparser.add_argument('--overwrite', '-f', action='store_true')

args = argparser.parse_args()

scrape = Scrape(file_root='race_today_result')

place_list = [arg.strip() for arg in args.list.split(',')]
overwrite = bool(args.overwrite)

for unit in place_list:
    place, kaisai, day = unit.split(':')

    for race_number_ in range(1, 13):
        race_round = '{:02d}'.format(race_number_)
        file_key = scrape.create_file_key(place, kaisai, day, race_round)

        url = scrape.create_url(file_key, 'result')

        try:
            # 既に存在している場合はsleepなしで次へ
            if overwrite:
                file_key = None
            if not scrape.fetch_result(url, file_key=file_key):
                continue
            scrape.sleep_by_sec(3)
        except Exception as e:
            # 何らかの例外が出たらログを出しておく
            scrape.log_dump('ERROR: {}'.format(e), level='WARN')
            scrape.log_dump('URL: {}'.format(url))
            scrape.sleep_by_sec(1)
