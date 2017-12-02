# -*- coding: utf-8 -*-

import sys
import json
import time
import os

predict = []
correct = []

"""
 0. dict_['id'],
 1. _round(dict_['weight'], -400, 100, 3),
 2. _round(dict_['diff'], 20, 40, 3),
 3. dict_['gender'],
 4. _round(dict_['handicap'], -50, 10, 3),
 5. dict_['jockey'],
 6. _round(dict_['odds'], -1, 199, 3),
 7. _round(dict_['ranking'], -1, 17, 3),
 8. _round(dict_['prev1'], -1, 17, 3),
 9. _round(dict_['prev2'], -1, 17, 3),
10. _round(dict_['prev3'], -1, 17, 3),
11. _round(dict_['prev4'], -1, 17, 3),
12. _round(dict_['prev5'], -1, 17, 3),
"""

p_ = None
c_ = None

limit = None

if len(sys.argv) == 2:
    limit = int(sys.argv[1])

count = 0

def float_to_int(float_):
    # -1-1の範囲を0 - 256に変更する
    # INT型の場合は無視する
    if isinstance(float_, int):
        return int(float_)
    return int((float_ + 1) * 128)


for line_ in sys.stdin:
    line = line_.rstrip()

    if line.startswith("#"):
        continue
    json_ = json.loads(line)

    if p_ is not None and c_ is not None:
        if len(p_) == len(c_):
            predict_ = []
            correct_ = []
            for unit in p_:
                unit_ = []
                for u in unit:
                    unit_.append(float_to_int(u))
                predict_.append(unit_)

            predict.extend(predict_)
            for unit in c_:
                # 3,2,1を1にまとめる
                if unit == 0:
                    correct_.append(0)
                else:
                    correct_.append(1)

            correct.extend(correct_)
        p_ = None
        c_ = None
        count += 1
        if limit == count:
            break
 
    if isinstance(json_[0], list):
        p_ = json_
    else:
        c_ = json_

t = int(time.time())

fname = 'data/log_{}'.format(t)
f = open(fname, 'w')

print(len(predict))
print(len(correct))

f.write(str(predict) + "\n")
f.write(str(correct))
f.close()
# print(predict)
# print(correct)
print(fname)
