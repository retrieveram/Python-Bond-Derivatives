## Pythonで学ぶ債券・金利デリバティブ <sub>*(QuantLib-Python 入門)*</sub>

### ダウンロード手順
- 上のファイル群はトップにある緑色の「<>Code」アイコンから「Download ZIP」の選択でダウンロード
- 拡張子ipynbがJupyter Notebook用のファイルで、myABBR.pyとmyUtil.pyはipynbと同じディレクトリに置くこと
- その他の拡張子pyのファイルは主にxlwings用

### QuantLibバージョン1.39へのコード修正 <sub>(Nov01,2025)</sub>

- 本書はQuantLibバージョン1.34(以下ver1.34等)で作動するコードを記載
- ver1.39での修正により、添付コードは次の各点で変更

  - 債券オブジェクトのbondYieldメソッドは仕様変更があり、A.1節記載のmyABBRモジュール 126行目で**債券価格クラス**を戻す<b>関数cP(...)</b>を設定(cPはclean priceの略)
    - 図4.2の13行目はこの関数により、97.0を<b>cP(97.0)</b>へ修正  
      (図4.13のzSpreadも同じ修正をいれた)
  - 図4.18の**AssetSwap**クラスはRFR指数に対する計算の場合、変動レグスケジュールを設定する仕様に変更。
    - これに対応するため、2行目で定義した空のfltSCH変数を次のように修正  
      fltSCH = ql.Schedule(settleDT, matDT, pdFreqA, calJP, unADJ,unADJ, dtGENb, EoMf)  
      (この引数は図4.2の9行目のbondSCDを多少修正したもの)
  - 図9.11の5行目**underlyingSwap**メソッドを**underlying**へ修正
    - もしver1.34で動かす場合、underlyingSwapへ戻すこと
- 上記修正により、添付コードはver1.39, 1.40で作動を確認済み
  - 各バージョンのインストール方法は添付したch00.ipynbの最初のセルを参照
- QuantLibの各バージョンの修正履歴は https://github.com/lballabio/QuantLib の右側中段のReleaseを参照


### その他 追記

- 図1.1表題と1ページ最後の行で「CalendarクラスのコンストラクタJapan」と表現したが、正確には「Calendarクラスを継承したJapanクラスのデフォルトコンストラクタJapan」が正しい。イントロダクションのため、難解な表現を避けた。
  - 同じ類の記述として、56ページでActual365Fixedを「DayCounterクラスのコンストラクタ」と称した。

- 10章 図10.7 のプレミアムレグ計算値のズレ  : Sep 2, 2025 調査中
  - 現時点ではmailing listからの回答は無し
  - C++のコードを確認するため、時間が必要

### 正誤表  


| ページ | 誤 | 正 |
|--------|----|----|
| 7 | 図1.1の13行目 | 図1.1の3行目 |
| 415 | 確率母関数 341 | 削除 |

