h3. 課題

* 馬体重が出てないケースがある
** 直前にならないと出ない
* オッズを素性から外す
** 強い素性になってしまう
* スクレイプする時にピュアなデータを引いてきて、手元で加工できるようにする
** ローカルに落として、素性化するのは後で

h3. ファイル
output.log : scrapeしたデータ
output_tmp.log: scrapeしたデータの一部
predict_base: 標準化済みの素性データ
race/XX_YY_ZZ_WW_int: レース毎の素性データ
- XX: 競馬場
- YY: 開催回数
- ZZ: 開催日数
- WW: レース番号
- _int: 標準化後

h3. 
* svm.py: svmのサンプル
* svm2.py: モデルを作成して評価
# cat data/log_1512184071 | python svm2.py
* svm_predict.py: モデルデータを利用して予測する
# python svm_predict.py data/log_1512188585 0.0005
# > race/07_04_01_08_int
* to_data.py: dataディレクトリ以下にタイムスタンプがついた標準化素性データが作成される
# cat output_tmp.log | python to_data.py
* to_data_by_race.py: １レースごとのデータを取得する
# for file in `ls race/ | grep -v int`;do python to_data_by_race.py race/${file};done
* scraping.py: まるっとスクレイプする
* scraping_specify_url.py: 対象のURLをスクレイプする（５柱のみ）
* scraping_specify_day.py: 対象の日付（開催会場、開催回数、開催日数）を指定してスクレイプする
# http_proxy= python scraping_specify_day.py "05:05:01, 09:05:01, 07:04:01"
# race/以下に05_05_01_XXとして出力される
