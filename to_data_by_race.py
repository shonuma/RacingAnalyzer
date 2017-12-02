# -*- coding: utf-8 -*-

import json
import sys
import time

p_ = None
c_ = None

limit = None


def float_to_int(float_):
    # -1-1の範囲を0 - 256に変更する
    # INT型の場合は無視する
    if isinstance(float_, int):
        return int(float_)
    return int((float_ + 1) * 128)


filename = sys.argv[1]

f = open(sys.argv[1], 'r')
for line_ in f:
    line = line_.rstrip()

    if line.startswith("#"):
        continue
    json_ = json.loads(line)

    if json_:
        predict_ = []
        for unit in json_:
            unit_ = []
            for u in unit:
                unit_.append(float_to_int(u))
            predict_.append(unit_)

t = int(time.time())

fname = '{}_int'.format(filename)
f = open(fname, 'w')

f.write(str(predict_))
f.close()
# print(predict)
# print(correct)
print(fname)
