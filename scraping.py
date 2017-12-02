# -*- coding: utf-8 -*-

import sys
from argparse import ArgumentParser

from libs.scrape import Scrape

usage = """
Usage: python {} [--place, -p <place>]

place: 01 - 10を指定。複数指定はカンマ。省略すると全て取得。

# URLの詳細
http://race.netkeiba.com/?pid=race&id=p201705050702&mode=top

# place
AA: 01 - 10
  01: 札幌, 02: 函館, 03: 福島, 04: 新潟, 05: 東京
  06: 中山, 07: 中京, 08: 京都, 09: 阪神, 10: 小倉

# kaisai
BB: 01 - ?
  開催回数

# day
CC: 01 - ?
  日数

# race_round
DD: 01 - 11 or 12
  レース番号

# 参考データ
- 札幌競馬　２開催１２日, 函館競馬　２開催１２日, 福島競馬　３開催２０日, 新潟競馬　３開催２６日, 東京競馬　５開催４５日
- 中山競馬　５開催４１日, 中京競馬　４開催２６日, 京都競馬　５開催４４日 ,阪神競馬　５開催４２日, 小倉競馬　２開催２０日

＃５柱
http://race.netkeiba.com/?pid=race&id=p201705050402&mode=shutuba

# 結果
http://race.netkeiba.com/?pid=race&id=p201705050402&mode=result
"""

argparser = ArgumentParser(usage=usage)
argparser.add_argument('--place', '-p', type=str, help='set place')
argparser.add_argument('--overwrite', '-f', action='store_true')

args = argparser.parse_args()

filter_by_place = []
if args.place:
    filter_by_place = [p.strip() for p in args.place.split(',')]

scrape = Scrape(file_root='race_all')

# 01, 02, 03, 04, 05, 06, 07, 08, 09, 10
for place in sorted(scrape.DESC_LIST.keys()):
    # 競馬場が指定されたら、そこしか取らない
    if filter_by_place and place not in filter_by_place:
        continue

    desc = scrape.DESC_LIST[place]

    kaisai_max = desc['kaisai']
    day_max = desc['day']
    for kaisai_ in range(1, kaisai_max+1):
        kaisai = '{:02d}'.format(kaisai_)
        for day_ in range(1, day_max+1):
            day = '{:02d}'.format(day_)
            for race_round_ in range(1, 13):
                race_round = '{:02d}'.format(race_round_)
                file_key = scrape.create_file_key(place,
                                                  kaisai,
                                                  day,
                                                  race_round)
                try:
                    # ５柱と結果を突き合わせる
                    for mode in ['shutuba', 'result']:
                        url = scrape.create_url(file_key, mode)

                        scrape.fetch_page(url, mode, file_key=file_key)
                        scrape.sleep_by_sec(2)
                except Exception as e:
                    # 何らかの例外が出たらログを出しておく
                    scrape.log_dump('ERROR: {}'.format(e), level='WARN')
                    scrape.log_dump('URL: {}'.format(url))
                    scrape.sleep_by_sec(2)
                else:
                    scrape.sleep_by_sec(3)
