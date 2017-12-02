# -*- coding: utf-8 -*-

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

desc_list = {
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
base = 'http://race.netkeiba.com/?pid=race&id=p2017{place}{kaisai}{day}{race_number}&mode={mode}'

# 体重のパターン
weight_pattern = re.compile('(\d+) \(([\+\-\d]+)\)')
ranking_pattern = re.compile('\((\d+)+')

# 馬の性別
gender_dict = {
    '牡': 0,
    '牝': 0.25,
    '騙': 0.5,
    'その他': 1,
}
jockey_dict = {}


def print_(message, level='INFO'):
    log_ = '# [{level}] {message}'.format(level=level,
                                          message=message)
    print(log_)
    sys.stderr.write(log_ + "\n")
    sys.stderr.flush()


def sleep_(sec):
    time.sleep(sec)
    sys.stdout.flush()


def rank_1():
    return 3


def rank_2():
    return 2


def rank_3():
    return 1


def rank_out():
    return 0


def to_predict_array(dict_):
    def _round(value, base, divide, round_index):
        return round((value + base) / divide, round_index)

    return [
        dict_['id'],
        # 体重: 400-500 で 0-1 にする
        _round(dict_['weight'], -400, 100, 3),
        # 増減: -20 - +20で 0-1にする
        _round(dict_['diff'], 20, 40, 3),
        # gender
        dict_['gender'],
        # ハンデ: 50 - 60で 0-1にする
        _round(dict_['handicap'], -50, 10, 3),
        # jockey
        dict_['jockey'],
        # odds: 1-200で0-1にする
        _round(dict_['odds'], -1, 199, 3),
        # ranking
        # 1-18で0-1にする
        _round(dict_['ranking'], -1, 17, 3),
        # prev1-5
        _round(dict_['prev1'], -1, 17, 3),
        _round(dict_['prev2'], -1, 17, 3),
        _round(dict_['prev3'], -1, 17, 3),
        _round(dict_['prev4'], -1, 17, 3),
        _round(dict_['prev5'], -1, 17, 3),
    ]


requests_ = requests.Session()

for place in range(1, 11):
# for place in range(1, 2):
    place_ = '{:02d}'.format(place)
    desc_ = desc_list[place_]
    kaisai_max = desc_['kaisai']
    day_max = desc_['day']
    for kaisai in range(1, kaisai_max+1):
    # for kaisai in range(1, 2):
        kaisai_ = '{:02d}'.format(kaisai)
        for day in range(1, day_max+1):
        # for day in range(1, 2):
            day_ = '{:02d}'.format(day)
            for race_number in range(1, 13):
            # for race_number in range(1, 3):
                try:
                    # ５柱と結果を突き合わせる
                    for mode in ['shutuba', 'result']:
                        # 素性の元を詰める箱
                        predict_list = []

                        # レース情報を取得
                        race_number_ = '{:02d}'.format(race_number)
                        url = base.format(place=place_,
                                          kaisai=kaisai_,
                                          day=day_,
                                          race_number=race_number_,
                                          mode=mode)

                        print_('URL:{}'.format(url))
                        response = requests_.get(url)
                        response.encoding = response.apparent_encoding
                        soup = BS4(response.text, 'html5lib')

                        if mode == 'shutuba':

                            trs = soup.find_all('table', {"class": "nk_tb_common"})[0].find_all('tr')
                            for tr in trs:
                                td_list = tr.find_all('td')
                                if not td_list:
                                    continue

                                # 馬番
                                id_ = int(td_list[1].text)

                                begin_data = 0
                                for index in range(3, len(td_list)): 
                                    if td_list[index].text.startswith('\n'):
                                        begin_data = index
                                        break

                                # 体重
                                w = td_list[index].text.split('\n')[-2]
                                weight_, diff_ = weight_pattern.match(w).groups()
                                # 性別、ハンデ、騎手
                                gender, handicap_, jockey \
                                    = td_list[index+1].text.split('\n')
                                # ヒットしなかったらその他
                                gender_ = gender_dict.get(gender) or 1
                                # 騎手の辞書を作る
                                if jockey_dict.get(jockey):
                                    jockey_ = jockey_dict[jockey]
                                else:
                                    jockey_id = len(jockey)
                                    jockey_dict.update({jockey_id: jockey})
                                    jockey_ = jockey_id
                                o = td_list[index+2].text.split('\n')
                                # オッズ、人気
                                odds_ = o[1]
                                ranking_ = ranking_pattern.match(o[2]).groups()[0]

                                # 前走5まで見る
                                history_index = index+3
                                prev_list = []
                                for i in range(0, 5):
                                    index = history_index + i
                                    if len(td_list) >= index:
                                        prev_list.append(0)
                                        continue
                                    prev = td_list[index]
                                    spans = prev.find_all('span')
                                    if not spans:
                                        prev_list.append(0)
                                        continue
                                    # 失格とかのケース
                                    try:
                                        order = int(spans[0].text)
                                    except:
                                        order = 0
                                    prev_list.append(order)

                                essential = {
                                    'id': id_,
                                    'weight': int(weight_),
                                    'diff': int(diff_),
                                    'gender': float(gender_),
                                    'handicap': int(handicap_),
                                    'jockey': jockey_,
                                    'odds': float(odds_),
                                    'ranking': int(ranking_),
                                    'prev1': prev_list[0],
                                    'prev2': prev_list[1],
                                    'prev3': prev_list[2],
                                    'prev4': prev_list[3],
                                    'prev5': prev_list[4],
                                }
                                essential_ = to_predict_array(essential)
                                predict_list.append(essential_)
                            # 出馬表を素性化
                            print(predict_list)

                        elif mode == 'result':
                            order = []
                            trs = soup.find_all('table', {"class": "nk_tb_common"})[0].find_all('tr')
                            result_list = []
                            for order in range(1, len(trs)):
                                result_list.append(rank_out())

                            td_list_1 = trs[1].find_all('td')
                            td_list_2 = trs[2].find_all('td')
                            td_list_3 = trs[3].find_all('td')
                            rank_1_ = int(td_list_1[2].text)
                            rank_2_ = int(td_list_2[2].text)
                            rank_3_ = int(td_list_3[2].text)
                            # indexは0から始まっているので1を引く
                            result_list[rank_1_-1] = rank_1()
                            result_list[rank_2_-1] = rank_2()
                            result_list[rank_3_-1] = rank_3()
                            print(result_list)
                    sleep_(3)

                except Exception as e:
                    # 何らかの例外が出たらログを出しておく
                    print_('ERROR: {}'.format(e), level='WARN')
                    print_('URL: {}'.format(url))
                else:
                    sleep_(10)
