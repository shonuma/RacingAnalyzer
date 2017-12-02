from __future__ import print_function

import itertools
import json
import sys

import matplotlib.pyplot as plt
import numpy as np
from sklearn import svm
from sklearn.datasets import load_digits
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV, train_test_split

# 手書き数字文字データセット(10class)
# digits = load_digits(n_class=10)
# 0, 1のみ
target_names = [0, 1]
# target_names = [0, 1, 2, 3]


# 特徴ベクトルと正解ラベル
# X, Y = digits.data, digits.target

for index, line_ in enumerate(sys.stdin):
    if index == 0:
        X = json.loads(line_.rstrip())
    elif index == 1:
        Y = json.loads(line_.rstrip())
    else:
        break

if not X or not Y:
    print('入力が足りません')
    sys.exit(0)

gamma = 0.0005
if len(sys.argv) > 1:
    gamma = float(sys.argv[1])

input_test = None
if len(sys.argv) > 2:
    # 予測ベクトルが書かれたファイルを入力
    try:
        f = open(sys.argv[2], 'r')
        for line_ in f:
            if line_.startswith('#'):
                continue
            input_test = json.loads(line_.rstrip())
            break

    except Exception as e:
        print(e)
        sys.exit(1)


# データセットを交差検証によって訓練データ・テストデータへ分割
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.4, random_state=0)

# 線形なSVMによる分類器（ソフトマージンにおける定数はC=1.）
# clf = svm.SVC(kernel='linear', C=1.)
clf = svm.SVC(kernel='rbf', gamma=gamma) # 非線形SVM, rbfカーネル

# 訓練データによる学習（超平面の決定）
clf.fit(x_train, y_train)


# input_testがある場合は、x_testを利用
if input_test:
    pred = clf.predict(input_test)
    print(pred)
    sys.exit(1)

# テストデータの分類
pred = clf.predict(x_test)

# for i in range(len(pred)):
#     print('{},{}.{}'.format(y_test[i],
#                             pred[i],
#                             y_test[i] == pred[i]))


# テストデータ分類精度
print ("Gamma: {}".format(gamma))
print ("Test Accuracy : ", (pred == y_test).mean())

#
# 混同行列（クラス分類の結果を可視化する行列）の表示
#

c_mat = confusion_matrix(y_test, pred)

print(c_mat)

"""
plt.imshow(c_mat, interpolation='nearest', cmap=plt.cm.Greens)

plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.grid(False)
plt.colorbar()
n_class = len(target_names)
marks = np.arange(n_class)
plt.xticks(marks, target_names)
plt.yticks(marks, target_names)

# 分類データ数テキストラベル
thresh = c_mat.max() / 2.
for i, c in enumerate(c_mat.flatten()):
    color = "yellow" if c > thresh else "black"
    plt.text(i / n_class, i % n_class, c, horizontalalignment="center", color=color)

plt.tight_layout()
plt.show()
"""
