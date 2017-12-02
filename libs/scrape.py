# -*- coding: utf-8 -*-

import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup as BS4

"""
http://race.netkeiba.com/?pid=race&id=p201705050702&mode=top
2017AABBCCDD&mode=top
AA: 01 - 10
  01: 札幌, 02: 函館, 03: 福島, 04: 新潟, 05: 東京
  06: 中山, 07: 中京, 08: 京都, 09: 阪神, 10: 小倉
BB: 01 - ?
  開催回数
CC: 01 - ?
  日数
DD: 01 - 11 or 12
  レース番号
参考データ
- 札幌競馬　２開催１２日, 函館競馬　２開催１２日, 福島競馬　３開催２０日, 新潟競馬　３開催２６日, 東京競馬　５開催４５日
- 中山競馬　５開催４１日, 中京競馬　４開催２６日, 京都競馬　５開催４４日 ,阪神競馬　５開催４２日, 小倉競馬　２開催２０日

＃５柱
http://race.netkeiba.com/?pid=race&id=p201705050402&mode=shutuba

# 結果
http://race.netkeiba.com/?pid=race&id=p201705050402&mode=result
"""

requests_ = requests.Session()


class Scrape:
    """netkeibaのページをScrapingする"""

    DESC_LIST = {
        '01': {'name': '札幌', 'kaisai': 2, 'day': 12},
        '02': {'name': '函館', 'kaisai': 2, 'day': 12},
        '03': {'name': '福島', 'kaisai': 3, 'day': 20},
        '04': {'name': '新潟', 'kaisai': 3, 'day': 26},
        '05': {'name': '東京', 'kaisai': 5, 'day': 45},
        '06': {'name': '中山', 'kaisai': 5, 'day': 41},
        '07': {'name': '中京', 'kaisai': 4, 'day': 26},
        '08': {'name': '京都', 'kaisai': 5, 'day': 44},
        '09': {'name': '阪神', 'kaisai': 5, 'day': 42},
        '10': {'name': '小倉', 'kaisai': 2, 'day': 20},
    }
    URL_BASE = 'http://race.netkeiba.com/?pid=race' \
        + '&id=p2017{place}{kaisai}{day}{race_round}&mode={mode}'

    # 体重のパターン
    WEIGHT_PATTERN = re.compile('(\d+) \(([\+\-\d]+)\)')
    RANKING_PATTERN = re.compile('\((\d+)+')

    # 馬の性別
    GENDER_DICT = {
        'その他': 0,
        '牡': 1,
        '牝': 2,
        'セ': 3,
    }
    JOCKET_DICT = {}

    MODE = [
        'shutuba',
        'result',
    ]

    def __init__(self, file_root=None):
        self._file_root = 'race_seed'
        if file_root:
            self._file_root = file_root

    def create_file_key(self, place, kaisai, day, race_round):
        return '_'.join([place, kaisai, day, race_round])

    def create_url(self, file_key, mode):
        place, kaisai, day, race_round = file_key.split('_')
        return Scrape.URL_BASE.format(place=place,
                                      kaisai=kaisai,
                                      day=day,
                                      race_round=race_round,
                                      mode=mode)

    def _fetch_url(self, url):
        self.log_dump('Fetch URL: {}'.format(url))
        response = requests_.get(url)
        response.encoding = response.apparent_encoding
        return BS4(response.text, 'html5lib')

    def fetch_page(self, url, mode, file_key=None):
        """モードを指定して紐づくページを取得"""
        if mode == 'shutuba':
            # print(url)
            return self.fetch_entry(url, file_key=file_key)
        elif mode == 'result':
            # print(url)
            return self.fetch_result(url, file_key=file_key)

    def fetch_result(self, url, file_key=None):
        """結果ページを取得する"""
        if file_key and self.file_exists(file_key, 'result'):
            self.log_dump('File Already Exists: {}'.format(file_key))
            return []
        soup = self._fetch_url(url)

        trs = soup.find_all('table',
                            {"class": "nk_tb_common"})[0].find_all('tr')

        result = [-1 for i in range(0, len(trs)-1)]
        for order, tr in enumerate(trs):
            td_list = tr.find_all('td')
            if not td_list:
                continue
            # 順位を取得する
            # 馬番順に順位を埋める
            result[int(td_list[2].text)-1] = int(order)-1

        if file_key:
            self.save_by_file(file_key, result, 'result')
        self.log_dump('SUCCESS URL: {}'.format(url))
        return result

    def fetch_entry(self, url, file_key=None):
        """出馬表ページを取得する"""
        if file_key and self.file_exists(file_key, 'shutuba'):
            self.log_dump('File Already Exists: {}'.format(file_key))
            return []

        predict_list = []
        soup = self._fetch_url(url)

        trs = soup.find_all('table',
                            {"class": "nk_tb_common"})[0].find_all('tr')
        for tr in trs:
            td_list = tr.find_all('td')
            if not td_list:
                continue
            # 枠番
            frame = int(td_list[0].text)
            # 馬番
            number = int(td_list[1].text)

            # 予想印(skipしてよい)
            for index in range(3, len(td_list)):
                if td_list[index].text.startswith('\n'):
                    break

            # 馬名セル
            name_cell = td_list[index]
            spans = name_cell.find_all('span')
            # 馬名
            name = spans[0].text
            # 親
            parent = []
            if len(spans) == 2:
                parent = spans[1].text.strip().split('\n')
            # 脚質
            # 01: 逃げ, 02: 先行, 03: 差し, 04: 追込
            racing_type = name_cell.find('img').attrs['src'].split('/')[-1]
            # 体重表記があれば追加する
            weight = 0
            weight_diff = 0
            strong_cell = name_cell.find('strong')
            if strong_cell:
                str_ = strong_cell.find('strong').text
                weight, weight_diff \
                    = Scrape.WEIGHT_PATTERN.match(str_).groups()

            # 斤量セル
            profile, handicap, jockey = td_list[index+1].text.split('\n')
            gender_and_age, color = profile.split('/')
            gender = Scrape.GENDER_DICT.get(profile[0]) or 0
            age = int(profile[1:])

            # オッズ
            o = td_list[index+2].text.split('\n')
            odds = o[1]
            ranking = Scrape.RANKING_PATTERN.match(o[2]).groups()[0]

            # 前走5まで見る
            history_index = index+3
            prev_list = []
            for i in range(history_index, history_index+5):
                spans = td_list[i].find_all('span')
                if not spans:
                    prev_list.append([])
                    continue
                prev_order = spans[0].text

            essential = [
                float(frame),  # 枠
                float(number),  # 馬番
                name,  # 馬名
                parent,  # 両親
                racing_type,  # 脚質
                float(weight),  # 体重
                float(weight_diff),  # 前回比
                float(gender),  # 性別
                float(age),  # 年齢
                color,  # 色
                float(handicap),  # 斤量
                jockey,  # 騎手
                float(odds),  # オッズ
                float(ranking),  # 人気
                prev_list[0],
                prev_list[1],
                prev_list[2],
                prev_list[3],
                prev_list[4],
            ]
            predict_list.append(essential)
        if file_key:
            self.save_by_file(file_key, predict_list, 'shutuba')
        self.log_dump('SUCCESS URL: {}'.format(url))
        return predict_list

    def log_dump(self, message, level='INFO'):
        log_ = '# [{level}] {message}'.format(level=level,
                                              message=message)
        print(log_)
        sys.stdout.flush()
        # sys.stderr.write(log_ + "\n")
        # sys.stderr.flush()

    def sleep_by_sec(self, sec):
        time.sleep(sec)
        sys.stdout.flush()

    def file_exists(self, file_key, mode):
        return os.path.exists(self._file_name(file_key, mode))

    def save_by_file(self, file_key, data, mode):
        f = open(self._file_name(file_key, mode), 'w')
        f.write(str(data))
        f.close()

    def _file_name(self, file_key, mode):
        return '{}/{}_{}.txt'.format(self._file_root, file_key, mode)
