## Pythonで学ぶ債券・金利デリバティブ <sub>*(QuantLib-Python 入門)*</sub>

### (a) ダウンロード方法、質問と要望
- 上のファイル群はトップにある緑色の「<>Code」アイコンから「Download ZIP」の選択でダウンロード
- 拡張子ipynbがJupyter Notebook用のファイルで、myABBR.pyとmyUtil.pyはipynbと同じディレクトリに置くこと
- その他の拡張子pyのファイルは主にxlwings用で、xlsmのExcelファイルと同じディレクトリに
- 質問や要望はQiita記事の最後の「コメント」欄でお願いします

### (b) Qiitaへの投稿記事
- [第1回：日本国債の特異体質とQuantLibによるJGBオブジェクト作成法](https://qiita.com/retrieveram/items/9ac277bbb4958e9e5d56) (Nov12,2025)
- [第2回：JGBクラスの日本式複利メソッドの実装 (using Brentクラス)](https://qiita.com/retrieveram/items/2956aec98842bbfae63b) (Nov20,2025)

### (c) 正誤表  

| ページ | 誤 | 正 |
|--------|----|----|
| 7 | 図1.1の13行目 | 図1.1の3行目 |
| 189の脚注17 | ギルサノフの定理の解説は、村上[13]等を参照 | ギルサノフの定理は9.9.1節で説明|
| 415 | 確率母関数 341 | 削除 |
- "プロパティ"という用語はテキストで示したものと異なるため、"プロパティ"は"メンバ変数"と読み替えてください
- "プロパティ"の定義はQiitaの第2回記事を参照

### (d) 追記

- 図1.1表題と1ページ最後の行で「CalendarクラスのコンストラクタJapan」と表現したが、正確には「Calendarクラスを継承したJapanクラスのデフォルトコンストラクタJapan」が正しい。イントロダクションのため、難解な表現を避けた
  - 同じ類の記述として、56ページでActual365Fixedを「DayCounterクラスのコンストラクタ」と呼んだ

- 10章 図10.7 のプレミアムレグ計算値のズレ  : Sep 2, 2025 調査中
  - 現時点ではmailing listからの回答は無し
  - C++のコードを確認するため、時間が必要

- "はじめに"章の脚注3に記した**Python in Excel**で利用できるライブラリはMicrosoftが選択したものに限定され、QuantLibは含まれていない

### (e) QuantLibバージョン1.39へのコード修正 <sub>(Nov01, 2025)</sub>

- 本書はQuantLibバージョン1.34(以下ver1.34等)で作動するコードを記載
- ver1.39のリリースにより、添付コードは次の各点で修正済み

  - bondYieldメソッドとその関連メソッドに仕様変更があり、A.1節記載のmyABBRモジュール 126行目で**債券価格クラス**を戻す<b>関数cP(...)</b>を設定 (cPはclean priceの略)
    - 図4.2の13行目はこの関数により、97.0を<b>cP(97.0)</b>へ修正
    - 図4.13のzSpreadメソッドも同じ理由で97.0をcP(97.0)へ修正
  - 図4.18の**AssetSwap**クラスはRFR指数に対する計算の場合、変動レグスケジュールを設定する仕様に変更。
    - この仕様変更のため、図4.18 2行目で定義した空のfltSCH変数を次のように修正  
      fltSCH = ql.Schedule(settleDT, matDT, pdFreqA, calJP, unADJ,unADJ, dtGENb, EoMf)  
      (この引数は図4.2の9行目のbondSCDを多少修正したもの)
    - 本来 **空のfltSCH変数**の指定によってアセットスワップされる債券のスケジュールを参照させた (つまり fltSCH=bondSCDに同じ)
  - 図9.11の5行目**underlyingSwap**メソッドは**underlying**へ変更 (もしver1.34で動かす場合、underlyingSwapへ戻さないとエラー)
- これらの修正により、上のコード群はver1.39, 1.40で作動を確認済み
  - QuantLibの各バージョンのインストール方法は添付ファイルch00.ipynbの最初のセルを参照
- QuantLibの各バージョンの修正履歴は https://github.com/lballabio/QuantLib の右側中段のReleaseを参照

### (f) もしJupyter Notebookで添付ファイルが動かない場合

- 新しいディレクトリで「Anaconda + VS Code + Jupyter Notebook」の組み合わせの場合、QuantLibやその他ライブライ(numpy)等が動かないケースが多々発生する。これはPCの中に複数のPythonをインストールした場合に起こる現象で、新しいディレクトリごとにPython環境(カーネル)が切り替わるため

- 対処法は次のステップ1, 2を実行すること

<b>(ステップ1)</b>   
- まず、右のコマンドをセルで実行。import sys ; sys.executable
- 表示されるパスが C:\Users\<ユーザー名>\AppData\Local\Programs\Python\...  
  Python3x\python.exe のような場合、Anacondaではない別のカーネルにアクセスしている。(このカーネルにはnumpy等もインストールされていないはず)

- 本来 Anacondaのpythonは次のようにAnaconda3がパスの中に現れる。  
  - C:\local\Anaconda3\python.exe や C:\local\Anaconda3\envs\base\python.exe 等

<b>(ステップ2)</b> 
- VS Codeで正しいカーネルを選択するには、VS Codeの右上にある<b>ガソリンスタンド</b>のアイコン(隣に"Python 3.1x.x"等を表示)をクリックし、base(Python 3.xx.x) \... \Anaconda3\... と表示されているカーネルを選び、Restartさせる (Anacondaのカーネルはbase...と表示される)
