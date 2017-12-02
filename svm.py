from __future__ import print_function

import itertools

import matplotlib.pyplot as plt
import numpy as np
from sklearn import svm
from sklearn.cross_validation import train_test_split
from sklearn.datasets import load_digits
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import confusion_matrix

# 手書き数字文字データセット(10class)
digits = load_digits(n_class=10)

# 特徴ベクトルと正解ラベル
X, Y = digits.data, digits.target

# データセットを交差検証によって訓練データ・テストデータへ分割
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.4, random_state=0)

# 線形なSVMによる分類器（ソフトマージンにおける定数はC=1.）
# clf = svm.SVC(kernel='linear', C=1.)
clf = svm.SVC(kernel='rbf', gamma=0.001) # 非線形SVM, rbfカーネル

# 訓練データによる学習（超平面の決定）
clf.fit(x_train, y_train)

# テストデータの分類
pred = clf.predict(x_test)

# テストデータ分類精度
print ("Test Accuracy : ", (pred == y_test).mean())


#
# 混同行列（クラス分類の結果を可視化する行列）の表示
#

c_mat = confusion_matrix(y_test, pred)

plt.imshow(c_mat, interpolation='nearest', cmap=plt.cm.Greens)

plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.grid(False)
plt.colorbar()
n_class = len(digits.target_names)
marks = np.arange(n_class)
plt.xticks(marks, digits.target_names)
plt.yticks(marks, digits.target_names)

# 分類データ数テキストラベル
thresh = c_mat.max() / 2.
for i, c in enumerate(c_mat.flatten()):
    color = "yellow" if c > thresh else "black"
    plt.text(i / n_class, i % n_class, c, horizontalalignment="center", color=color)

plt.tight_layout()
plt.show()
