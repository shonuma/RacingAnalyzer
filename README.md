## 課題

* 馬体重が出てないケースがある
** 直前にならないと出ない
* オッズを素性から外す
** 強い素性になってしまう
* スクレイプする時にピュアなデータを引いてきて、手元で加工できるようにする
** ローカルに落として、素性化するのは後で

0. ID
1. 枠番
2. 性別、年齢、斤量、騎手、(体重)
3. オッズ
4. 人気
5. 前走1
6. 前走2
7. 前走3
8. 前走4
9. 前走5

[[1,
1,
'牝6/鹿\n54\n武士沢',
70.1,
7,
'\n\n17.11.04\xa0東京\n10\n\nノベンバー１６００下\n芝2000\xa02:01.4\xa0良\n\n14頭5番14人\xa0武士沢友52.0\n10-11-11\xa0(33.6)\xa0\xa0480(-4)\nストーンウェア(0.5)\n\n\n',
'\n\n17.10.09\xa0東京\n10\n\n六社Ｓ１６００下\n芝2400\xa02:26.1\xa0良\n\n12頭12番11人\xa0勝浦正樹52.0\n12-12-12-10\xa0(34.9)\xa0\xa0484(-2)\nブライトバローズ(1.0)\n\n\n',
'\n\n17.08.26\xa0札幌\n13\n\nＷＡＳＪ２１６００下\n芝2000\xa02:02.9\xa0良\n\n14頭11番3人\xa0Ｍ．デム56.0\n14-14-14-14\xa0(36.7)\xa0\xa0486(+2)\nクロコスミア(1.9)\n\n\n',
'\n\n17.08.05\xa0札幌\n4\n\n札幌日経ＯOP\n芝2600\xa02:40.8\xa0良\n\n10頭2番7人\xa0勝浦正樹54.0\n8-8-8-5\xa0(35.1)\xa0\xa0484(-4)\nモンドインテロ(0.2)\n\n\n',
'\n\n17.07.15\xa0福島\n1\n\n信夫山特別１０００下\n芝2600\xa02:39.6\xa0良\n\n10頭3番8人\xa0武士沢友51.0\n9-10-7-6\xa0(35.1)\xa0\xa0488(-2)\nワイルドダンサー(-0.1)\n\n\n'],




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
