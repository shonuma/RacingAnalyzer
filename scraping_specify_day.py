# -*- coding: utf-8 -*-

import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup as BS4

"""
引数に競馬場、開催、日数のリスト(05:05:01, 09:05:01, 07:04:01)を指定する
- 中山(05) 5回(05) 1日目(01)
- 阪神(09) 5回(09) 1日目(01)
- 中京(07) 4回(04) 1日目(01)

python scraping_specify_day.py 05,09,07
"""
place_list = [arg.strip() for arg in sys.argv[1].split(',')]

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

for unit in place_list:
    place_, kaisai_, day_ = unit.split(':')
    file_key = '_'.join(unit.split(':'))

    for race_number in range(1, 13):
    # for race_number in range(1, 3):
        try:
            # ５柱のみ取得
            for mode in ['shutuba']:
                # 素性の元を詰める箱
                predict_list = []

                # レース情報を取得
                race_number_ = '{:02d}'.format(race_number)
                file_key_ = file_key + '_' + race_number_

                url = base.format(place=place_,
                                  kaisai=kaisai_,
                                  day=day_,
                                  race_number=race_number_,
                                  mode=mode)

                # 作成済みならスルー
                if os.path.exists('race/{}'.format(file_key_)):
                    print_('ALREADY COMPLETED URL: {}'.format(url))
                    continue

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
                    f = open('race/{}'.format(file_key_), 'w')
                    f.write(str(predict_list))
                    f.close()
                    print(predict_list)

        except Exception as e:
            # 何らかの例外が出たらログを出しておく
            print_('ERROR: {}'.format(e), level='WARN')
            print_('URL: {}'.format(url))
        else:
            sleep_(1)
