## Pythonで学ぶ債券・金利デリバティブ <sub>*(QuantLib-Python 入門)*</sub>

### (a) ダウンロード方法、質問と要望
- 上のファイル群はトップにある緑色の`<>Code`アイコンから`Download ZIP`の選択でダウンロード
- 拡張子`ipynb`がJupyter Notebook用のファイルで、`myABBR.py`と`myUtil.py`はipynbと同じディレクトリに置く
- その他の拡張子`py`のファイルは主にxlwings用で、Excelファイルと同じディレクトリに置く
  - (別のディレクトリに置く方法はch00.ipynb ファイルの補足1を参照)
- myABBR.pyとmyUtil.pyは随時更新予定。ファイル名に"オリジナル"とあるファイルが補足章と同じもの
- 質問や要望はQiita記事の最後の「コメント」欄へ

### (b) Qiitaへの投稿記事
- [第1回：日本国債の特異体質とQuantLibによるJGBオブジェクト作成法](https://qiita.com/retrieveram/items/9ac277bbb4958e9e5d56) (Nov12,2025)
- [第2回：JGBクラスの日本式複利メソッドの実装 (using Brentクラス)](https://qiita.com/retrieveram/items/2956aec98842bbfae63b) (Nov20,2025)
- [第3回：シリアルFRAを持つTiborカーブの構築](https://qiita.com/retrieveram/items/67245bcd3e9ef5353c43)  (Dec22,2025)
- [第4回：Hagan-West流 の Tiborカーブ構築](https://qiita.com/retrieveram/items/f0f8550120d66ada8463)  (Dec27,2025)

### (c) 正誤表  

| ページ | 誤 | 正 |
|--------|----|----|
| 7 | 図1.1の13行目 | 図1.1の3行目 |
| 189の脚注17 | ギルサノフの定理の解説は、村上[13]等を参照 | ギルサノフの定理は9.9.1節で説明|
| 415 | 確率母関数 341 | 削除 |
- **プロパティ**という用語はテキストで示したものと異なるため、"プロパティ"は**メンバ変数**と読み替えてください
- "プロパティ"の定義はQiitaの第2回記事を参照

### (d) 追記

- 図1.1表題と1ページ最後の行で「CalendarクラスのコンストラクタJapan」と表現したが、正確には「Calendarクラスを継承したJapanクラスのデフォルトコンストラクタJapan」が正しい。イントロダクションのため、難解な表現を避けた
  - 同じ類の記述として、56ページで`Actual365Fixed`を「DayCounterクラスのコンストラクタ」と呼んだ

- 10章 図10.7 のプレミアムレグ計算値のズレ  : Sep 2, 2025 調査中
  - 現時点ではmailing listからの回答は無し
  - C++のコードを確認するため、時間が必要

- "はじめに"章の脚注3に記した`Python in Excel`で利用できるライブラリはMicrosoftが選択したものに限定され、`QuantLib`は含まれていない

- QuantLibの仕様変更への対応は該当するコードに注記した
