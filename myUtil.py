from myABBR import *
from scipy.stats import norm
  
##### ショートカット #####
# シンプルクォート
def sqHDL(xx):   
  '''sqHDL(xx)=ql.QuoteHandle(ql.SimpleQuote(xx))''' 
  return ql.QuoteHandle(ql.SimpleQuote(xx))

# フラットフォワード ** OBJとTSHの2つを戻す点に注意  **
def ffTSH(settleDT, rate, dc=dcA365, cmpd=2, freq=1):   
  '''ffTSH(settleDT,rate,dc=dcA365,cmpd=2,freq=1) 
                                    = ffCrvOBJ,ql.YTS(ql.FlatForward(...))
     cmpd=2:Continuous, 1:Compounded freq=1:Annual 2:Semiannual''' 
  ffCrvOBJ = ql.FlatForward(settleDT, rate, dc, cmpd, freq)
  ffCrvOBJ.enableExtrapolation()
  return ffCrvOBJ, ql.YieldTermStructureHandle(ffCrvOBJ)

# ブラックコンスタントボラTSハンドル
def bVolTSH(tradeDT, vol, cal=calWK, dc=dcA365):   
  '''bVolTSH(tradeDT, vol, cal=calWK, dc=dcA365)
                                    =ql.BlackVolTSH(ql.BlackConstantVol(...))''' 
  return ql.BlackVolTermStructureHandle(
                    ql.BlackConstantVol(tradeDT, cal, vol, dc))

##### 各種カーブオブジェクト作成 #####
# SOFRカーブ 
def makeSofrCurve(crvDATA):
    '''makeSofrCurve(crvDATA)->[sofrIX,sfCrvOBJ,sfCrvHDL,sfParRT]'''      
  # 1.指標金利オブジェクトと初期値設定
    sfCrvHDL = ql.RelinkableYieldTermStructureHandle()  
    sofrIX = ql.Sofr(sfCrvHDL)
  # 2. HelperとSOFRカーブオブジェクト
    cHelper, sfParRT = [], []
    for knd, tnr, rt in crvDATA:  # tnr=(0:month,1:year,2:freq) for futures
        if knd == 'depo':
            if ql.Period(tnr).length() == 1:
                cHelper.append(ql.DepositRateHelper(sqHDL(rt/100),sofrIX)) 
        if knd == 'fut': cHelper.append(
            ql.SofrFutureRateHelper(sqHDL(rt),tnr[0],tnr[1],tnr[2]))
        if knd == 'swap': cHelper.append(
            ql.OISRateHelper(Tp2, ql.Period(tnr),sqHDL(rt/100),sofrIX))
        sfParRT.append(rt/100)                             # パーレート用リスト
    sfCrvOBJ = ql.PiecewiseLogLinearDiscount(Tp0, calUSs, cHelper, dcA360)
    sfCrvHDL.linkTo(sfCrvOBJ) ; sfCrvOBJ.enableExtrapolation()
    return sofrIX, sfCrvOBJ, sfCrvHDL, sfParRT
  
# TONAカーブ
def makeTonaCurve(crvDATA):
    '''makeTonaCurve(crvDATA)->[tonaIX,tnCrvOBJ,tnCrvHDL,tnParRT]'''
  # 1.指標金利オブジェクト
    tnCrvHDL = ql.RelinkableYieldTermStructureHandle()  
    tonaIX = ql.OvernightIndex('TONA', Tp0,  jpyFX, calJP, dcA365, tnCrvHDL)
  # 2. カーブヘルパー
    cHelper, tnParRT = [], []
    for knd, tnr, rt in crvDATA:
      if knd == 'depo':
          cHelper.append(ql.DepositRateHelper(sqHDL(rt/100),tonaIX)) 
      if knd == 'swap':
          cHelper.append(ql.OISRateHelper(Tp2, pD(tnr), sqHDL(rt/100),tonaIX))
      tnParRT.append(rt/100)                                # パーレート用リスト
  # カーブオブジェクト
    tnCrvOBJ = ql.PiecewiseLogLinearDiscount(Tp0, calJP, cHelper, dcA365)
    tnCrvHDL.linkTo(tnCrvOBJ) ; tnCrvOBJ.enableExtrapolation()
    return tonaIX, tnCrvOBJ, tnCrvHDL, tnParRT
  
# ESTRカーブ
def makeEstrCurve(crvDATA):
  '''makeEstrCurve(crvDATA)->[esIX,esCrvOBJ,esCrvHDL,esParRT]'''
  # 1.指標金利オブジェクトと初期値設定
  esCrvHDL = ql.RelinkableYieldTermStructureHandle()  
  esIX     = ql.Estr(esCrvHDL)
  # 2. HelperとSOFRカーブオブジェクト
  cHelper, esParRT = [], []
  for knd, tnr, rt in crvDATA:
      if knd == 'depo':
          cHelper.append(ql.DepositRateHelper(sqHDL(rt/100),esIX)) 
      if knd == 'swap':
          cHelper.append(ql.OISRateHelper(Tp2,pD(tnr),sqHDL(rt/100),esIX))
      esParRT.append(rt/100)                             # パーレート用リスト
  # カーブオブジェクト      
  esCrvOBJ = ql.PiecewiseLogLinearDiscount(Tp0, calEU, cHelper, dcA360)
  esCrvHDL.linkTo(esCrvOBJ) ; esCrvOBJ.enableExtrapolation()
  return esIX, esCrvOBJ, esCrvHDL, esParRT

def makeTonaCurve(crvDATA):
    '''makeTonaCurve(crvDATA)->[tonaIX,tnCrvOBJ,tnCrvHDL,tnParRT]'''
  # 1.指標金利オブジェクト
    tnCrvHDL = ql.RelinkableYieldTermStructureHandle()  
    tonaIX = ql.OvernightIndex('TONA', Tp0, jpyFX, calJP, dcA365, tnCrvHDL)
  # 2. カーブヘルパー
    cHelper, tnParRT = [], []
    for knd, tnr, rt in crvDATA:
      if knd == 'depo':
          cHelper.append(ql.DepositRateHelper(sqHDL(rt/100),tonaIX)) 
      if knd == 'swap':
          cHelper.append(ql.OISRateHelper(Tp2, pD(tnr), sqHDL(rt/100),tonaIX))
      tnParRT.append(rt/100)                                # パーレート用リスト
  # カーブオブジェクト
    tnCrvOBJ = ql.PiecewiseLogLinearDiscount(Tp0, calJP, cHelper, dcA365)
    tnCrvHDL.linkTo(tnCrvOBJ) ; tnCrvOBJ.enableExtrapolation()
    return tonaIX, tnCrvOBJ, tnCrvHDL, tnParRT
  
# TIBORカーブ
def makeTiborCurve(crvDATA):
    '''makeTiborCurve(crvDATA)->[tbrIX,tbCrvOBJ,tbCrvHDL,tbParRT]'''
  # 1.指標金利オブジェクト
    tbCrvHDL = ql.RelinkableYieldTermStructureHandle() 
    tbrIX    = ql.Tibor(pdFreqSA, tbCrvHDL)
  # 2. HelperとTiborカーブオブジェクト
    cHelper, tbParRT = [], []
    for knd, tnr, rt in crvDATA:
       if knd == 'depo': cHelper.append(ql.DepositRateHelper(sqHDL(rt/100),     tbrIX)) 
       if knd == 'fra' : cHelper.append(ql.FraRateHelper (sqHDL(rt/100),pD(tnr),tbrIX)) 
       if knd == 'swap': cHelper.append(ql.SwapRateHelper(sqHDL(rt/100),pD(tnr), 
                                                   calJP, frqSA, mFLLW, dcA365, tbrIX))
       tbParRT.append(rt/100)                            # パーレート用リスト
    tbCrvOBJ = ql.PiecewiseLogLinearDiscount(Tp2, calJP, cHelper, dcA365)
    tbCrvHDL.linkTo(tbCrvOBJ) ; tbCrvOBJ.enableExtrapolation()
    return tbrIX, tbCrvOBJ, tbCrvHDL, tbParRT

# Euriborカーブ
def makeEuriborCurve(crvDATA):
    '''makeEuriborCurve(crvDATA)->[ebrIX,ebCrvOBJ,ebCrvHDL,ebParRT]'''    
  # 1.指標金利オブジェクト
    ebCrvHDL = ql.RelinkableYieldTermStructureHandle() 
    ebrIX    = ql.Euribor(pdFreqSA, ebCrvHDL)
  # 2. HelperとTONAカーブオブジェクト
    cHelper, ebParRT = [], []
    for knd, tnr, rt in crvDATA:
       if knd == 'depo': cHelper.append(ql.DepositRateHelper(sqHDL(rt/100),ebrIX)) 
       if knd == 'swap': cHelper.append(ql.SwapRateHelper(   sqHDL(rt/100),
                                       pD(tnr), calEU, frqA, mFLLW, dc30, ebrIX))
       ebParRT.append(rt/100)                            # パーレート用リスト
    ebCrvOBJ = ql.PiecewiseLogLinearDiscount(Tp2, calEU, cHelper, dc30)
    ebCrvHDL.linkTo(ebCrvOBJ) ; ebCrvOBJ.enableExtrapolation()
    return ebrIX, ebCrvOBJ, ebCrvHDL, ebParRT
  
# アニュイティ計算
def calcAnnuity(annSCD, crvOBJ, dc=dcA365): 
    '''calcAnnuity(annuitySCD, curveOBJ, dc=dcA365) -> Annuity)'''
    discFCT = nA([crvOBJ.discount(xx) for xx in annSCD][1:])
    tnrLST  = np.diff([dc.yearFraction(annSCD.startDate(), xx) for xx in annSCD]) 
    return np.sum(tnrLST * discFCT) 

##### Swap/債券/CDSキャッシュフロー表 #####
# Swap
def swapCashFlow(swapOBJ, curveOBJ, leg=1, dc=dcA365): 
    '''swapCashFlow(swapOBJ, curveOBJ, leg=1:FLoat  0:Fix)-> DataFrame)''' 
    settleDT = curveOBJ.referenceDate() 
    if leg == 1:  # 変動ﾚｸﾞ leg(1)
        dfSWP = pd.DataFrame({
            'fixingDate': cpn.fixingDate().ISO(),
            'accruStart': cpn.accrualStartDate(),                # No ISO form
            'accruEnd':   cpn.accrualEndDate(),                  # No ISO form
            'payDate':    cpn.date(),                            # No ISO form
            'days':       dc.dayCount(cpn.accrualStartDate(),cpn.accrualEndDate()),
            'rate':       cpn.rate(),
            'spread':     cpn.spread(),
            'amount':     cpn.amount(),
            } for cpn in map(ql.as_floating_rate_coupon, swapOBJ.leg(1)))
        # マルチカーブのフォワード                                  1000は便宜上の数字
        fwdRT = [curveOBJ.forwardRate(                         
                        dfSWP.accruStart[id],dfSWP.accruEnd[id], dcA365, SPL).rate()
                      if settleDT < dfSWP.accruStart[id] else 1000 for id in dfSWP.index ] 
        dfSWP = pd.concat([dfSWP, pd.DataFrame(fwdRT, columns=['fwdRT']) ], axis=1)
        dfSWP.rate= dfSWP.rate.where(dfSWP.fwdRT>999, dfSWP.fwdRT)
        dfSWP = dfSWP.drop('fwdRT', axis=1)
        dfSWP.accruStart = dfSWP.accruStart.map(lambda x: x.ISO())
        dfSWP.accruEnd = dfSWP.accruEnd.map(lambda x: x.ISO())
    else:          # 固定ﾚｸﾞ leg(0)
        dfSWP = pd.DataFrame({
            'nominal':    cpn.nominal(),
            'accruStart': cpn.accrualStartDate().ISO(),
            'accruEnd':   cpn.accrualEndDate().ISO(),
            'payDate':    cpn.date(),
            'days':       dc.dayCount(cpn.accrualStartDate(),cpn.accrualEndDate()),
            'rate':       cpn.rate(),
            'amount':     cpn.amount()
            } for cpn in map(ql.as_fixed_rate_coupon, swapOBJ.leg(0)))
    # 起算日の挿入
    dfEFF = pd.DataFrame([{'payDate': swapOBJ.startDate()}], columns=dfSWP.columns)
    dfSWP = pd.concat([dfEFF, dfSWP], ignore_index=True)                
    # ディスカウントファクター(DF)
    psDF = [1.0                   for dt in dfSWP.payDate if dt <= settleDT] # past   DF
    fuDF = [curveOBJ.discount(dt) for dt in dfSWP.payDate if settleDT < dt ] # future DF
    dfSWP = pd.concat([dfSWP, pd.DataFrame(psDF+fuDF, columns=['DF']) ], axis=1)
    dfSWP.payDate = dfSWP.payDate.map(lambda x: x.ISO())                        # ISOへ
    return dfSWP

# 債券 (past=0は過去キャッシュフローの非表示)
def bondCashFlow(bondOBJ, ir='', yts='', past=0):    
    '''1:(ir='',yts='')=No DF      2:(ir=irOBJ, yts='')=ir DF
       3:(ir='', yts=ytOBJ)=yt DF  
       4:( , ,past=0)=futureCF      5:( , ,past=1)=past+futureCF    '''
    dfCPN = pd.DataFrame({
        'payDate':    cpn.date(),          # no ISO
        'coupon':     cpn.rate(),
        'accruStart': cpn.accrualStartDate().ISO(),
        'accruEnd':   cpn.accrualEndDate().ISO(),
        'amount':     cpn.amount(),
        } for cpn in map(ql.as_coupon, bondOBJ.cashflows()) if cpn is not None )
    # 起算日, 元本
    dfEFF = pd.DataFrame([{'payDate': bondOBJ.startDate()}], columns=dfCPN.columns)
    dfPRN = pd.DataFrame({'payDate': cf.date(), 'amount':cf.amount()} for cf,cpn 
                in zip(bondOBJ.cashflows(),map(ql.as_coupon, bondOBJ.cashflows())) 
                                                                if cpn is None )
    dfBND = pd.concat([dfEFF, dfCPN, dfPRN], ignore_index=True) 
    # ディスカウントファクター列作成
    settleDT = bondOBJ.settlementDate()
    psDF = [1.0       for dt in dfBND.payDate if dt <= settleDT]     #past DF
    # future DF
    if ir != '' and yts == '' :                                     # irtOBJ
      fuDF = [ir.discountFactor(settleDT, dt)
                      for dt in dfBND.payDate if settleDT < dt ] 
      dfBND = pd.concat([dfBND, pd.DataFrame(psDF+fuDF, columns=['DF']) ], axis=1)
    elif yts != '' :                                                  # ytsOBJ
      fuDF = [yts.discount(dt)
                      for dt in dfBND.payDate if settleDT < dt ] 
      dfBND = pd.concat([dfBND, pd.DataFrame(psDF+fuDF, columns=['DF']) ], axis=1)
    # 将来キャッシュフローの抽出
    if past == 0: 
      dfBND = dfBND[dfBND.payDate >= settleDT]
      dfBND = dfBND.reset_index(drop=True)              #インデックス番号リセット
    dfBND.payDate  =  dfBND.payDate.map(lambda x: x.ISO())  # ISOフォーマットへ
    return dfBND

# 物価連動債 (past=0は過去キャッシュフローの非表示)
def cpiBondCashFlow(bondOBJ, ir='', yts='', past=0):    
    '''1:(ir='',yts='')=No DF      2:(ir=irOBJ, yts='')=ir DF
       3:(ir='', yts=ytOBJ)=yt DF  
       4:( , ,past=0)=futureCF      5:( , ,past=1)=past+futureCF    '''
    dfCPN = pd.DataFrame({
        'payDate':    cpn.date(),          # no ISO
        'accruStart': cpn.accrualStartDate().ISO(),
        'accruEnd':   cpn.accrualEndDate().ISO(),
        'cpi':        cpn.indexFixing(),
        'coupon':     cpn.rate(),        
        'amount':     cpn.amount(),
        } for cpn in map(ql.as_cpi_coupon, bondOBJ.cashflows()) if cpn is not None )
    # 起算日, 元本
    dfEFF = pd.DataFrame([{'payDate': bondOBJ.startDate()}], columns=dfCPN.columns)
    dfPRN = pd.DataFrame({'payDate': cf.date(), 'amount':cf.amount()} for cf,cpn 
            in zip(bondOBJ.cashflows(),map(ql.as_cpi_coupon, bondOBJ.cashflows())) 
                                                                if cpn is None )
    dfBND = pd.concat([dfEFF, dfCPN, dfPRN], ignore_index=True) 
    # ディスカウントファクター列作成
    settleDT = bondOBJ.settlementDate()
    psDF = [1.0       for dt in dfBND.payDate if dt <= settleDT]     #past DF
    # future DF
    if ir != '' and yts == '' :                                     # irtOBJ
      fuDF = [ir.discountFactor(settleDT, dt)
                      for dt in dfBND.payDate if settleDT < dt ] 
      dfBND = pd.concat([dfBND, pd.DataFrame(psDF+fuDF, columns=['DF']) ], axis=1)
    elif yts != '' :                                                  # ytsOBJ
      fuDF = [yts.discount(dt)
                      for dt in dfBND.payDate if settleDT < dt ] 
      dfBND = pd.concat([dfBND, pd.DataFrame(psDF+fuDF, columns=['DF']) ], axis=1)
    # 将来キャッシュフローの抽出
    if past == 0: 
      dfBND = dfBND[dfBND.payDate >= settleDT]
      dfBND = dfBND.reset_index(drop=True)              #インデックス番号リセット
    dfBND.payDate  =  dfBND.payDate.map(lambda x: x.ISO())  # ISOフォーマットへ
    return dfBND

# CDS
def cdsCashFlow(cdsOBJ, hzCvOBJ, dsCvOBJ):
    '''cdsCashFlow(cdsOBJ, hzCvOBJ, dsCvOBJ)-> DataFrame)'''    
    tradeDT, ntlAMT = cdsOBJ.tradeDate(), cdsOBJ.notional() 
    dfCDS = pd.DataFrame({
        'payDate':    cpn.date(),
        'coupon':     cpn.rate(),
        'accStt':     cpn.accrualStartDate().ISO(),
        'accEnd':     cpn.accrualEndDate(),
        'days':       cpn.amount()/(ntlAMT*cpn.rate()    /360),
        'YF':         cpn.amount()/(ntlAMT*cpn.rate()*365/360),
        'amount':     cpn.amount(),
        } for cpn in map(ql.as_coupon, cdsOBJ.coupons()))
    # 起算日の挿入
    dfEFF = pd.DataFrame([{'payDate': cdsOBJ.protectionStartDate(), 
                    'accEnd': cdsOBJ.protectionStartDate()}], columns=dfCDS.columns)
    dfCDS = pd.concat([dfEFF, dfCDS], ignore_index=True)            
    #ディスカウントファクター
    psDF  = [1.0                  for dt in dfCDS.payDate if dt <= tradeDT] #past   DF
    fuDF  = [dsCvOBJ.discount(dt) for dt in dfCDS.payDate if tradeDT < dt ] #future DF
    dfCDS = pd.concat([dfCDS, pd.DataFrame(psDF+fuDF, columns=['DF']) ], axis=1)
    #生存確率QとdQ
    psQ   = [1.0                             for dt in dfCDS.accEnd if dt <= tradeDT]
    fuQ   = [hzCvOBJ.survivalProbability(dt) for dt in dfCDS.accEnd if tradeDT < dt ]
    dfCDS = pd.concat([dfCDS, pd.DataFrame(psQ+fuQ, columns=['Q']) ], axis=1) 
    dQ    = np.insert(np.diff(dfCDS.Q)*(-1), 0, 0) 
    dfCDS = pd.concat([dfCDS, pd.DataFrame( dict(dQ=dQ)) ], axis=1) 
    # mid計算
    midDTs  = dfCDS.payDate[:-1]+(np.diff(dfCDS.payDate)/2).astype('int')
    midDFs  = [dsCvOBJ.discount(dd) for dd in midDTs]
    midQs   = [hzCvOBJ.survivalProbability(dd) for dd in midDTs]
    dfDFQm  = pd.DataFrame( dict(mDate=midDTs, mDF=midDFs, mQ=midQs))
    dfDFQm.mDate = dfDFQm.mDate.map(lambda x: x.ISO())
    dfDFQm  = pd.concat([pd.DataFrame(columns=['mDate'],index=[0]),     #空の行を追加
                                                        dfDFQm],ignore_index=True)
    dfCDS   = pd.concat([dfCDS, dfDFQm ], axis=1)  
    #日付修正(ISOフォーマット)
    dfCDS.payDate =  dfCDS.payDate.map(lambda x:x.ISO())
    dfCDS.accEnd  =  dfCDS.accEnd.map(lambda x:x.ISO())
    return dfCDS

##### 債券オブジェクト 作成関数 ##### 
# テキスト143ページとは異なり、effDT,matDT はql.Date型、cpnRTは実数に変更
# 関数から戻されるオブジェクトは nOBJ=1,2,3 で指定
def makeJGB(effDT, matDT, cpnRT, faceAMT=100.0, nOBJ=1):
    jgbSCD = ql.Schedule(effDT,matDT,pdFreqSA,calNL,unADJ,unADJ,dtGENb,EoMf)
    jgbOBJ = JGB(Tp1, faceAMT, jgbSCD, [cpnRT], dcA365n)
    jgbOBa = JGB(Tp1, faceAMT, jgbSCD, [cpnRT], dcA365 )
    if   nOBJ==3: return jgbOBJ, jgbSCD, jgbOBa
    elif nOBJ==2: return jgbOBJ, jgbSCD
    else        : return jgbOBJ

def makeUsTsy(effDT, matDT, cpnRT, faceAMT=100.0, nOBJ=1):
    tsySCD = ql.Schedule(effDT,matDT,pdFreqSA,calNL,unADJ,unADJ,dtGENb,EoMt)
    tsyOBJ = ql.FixedRateBond(Tp1, faceAMT, tsySCD, [cpnRT], dcAAb)
    if nOBJ==2: return tsyOBJ, tsySCD
    else      : return tsyOBJ

##### JGB クラス #####    
# ・matDSで使うsettlementDate()はevaluationDateで変わるため、
#   matDSは動的な計算が必要。
# ・@propertyはメソッド(メンバ関数)をメンバ変数のように
#   見せるデコレータで、matDSメソッドは使用される毎に再計算する。
# ・メンバ変数のself.cpnRTは初期値固定で十分。(再計算の必要なし)
class JGB(ql.FixedRateBond):
    def __init__(self, settDS, faceAMT, bondSCD,cpn, dcBond, 
                 paymentConvention=ql.Following,
                 redemption=100.0, issueDate=ql.Date()      ):
      super().__init__(settDS, faceAMT, bondSCD, cpn, dcBond, 
                 paymentConvention, redemption, issueDate   )
      self.cpnRT = ql.as_coupon(self.cashflows()[0]).rate()
    # self.matDS = dcA365n.dayCount(self.settlementDate(), ...)

    @property
    def matDS(self):
      return dcA365n.dayCount(self.settlementDate(), self.maturityDate())

    def SimplePrice(self, sYLD):                # 100円当りの価格
        return 100*(365+self.cpnRT*self.matDS)/(365+sYLD*self.matDS)

    def SimpleYield(self, clnPR):                # 実数を戻す
        return  ( 100*(365+ self.cpnRT*self.matDS)/clnPR - 365 )/self.matDS
    
    def JapanCompoundYield(self, clnPR):
      sYLD = self.SimpleYield(clnPR) 
      def prSLVR(yld):
          CY  = self.cpnRT / yld
          DF  = (1 + yld/frqSA)**(-self.matDS*frqSA/365)
          PRC = 100*( CY + DF*(1-CY) )
          return PRC - clnPR
                                   # accuracy guess xMin  xMax 
      return ql.Brent().solve(prSLVR, 1e-6,   sYLD, -0.1, 1.0)
    
##### ノーマルモデル クラス #####
class normalCalculator:
    ''' Bachelier normal model class
        normalCalculator(payOffObj, matDT, futRT, volRT, rfOBJ)    
        matYR:満期日, SD:Standard Deviation,  DF:discFactor.'''

    def __init__(self, payOffObj, matDT, futRT, volRT, rfOBJ):
      # 満期年
      self.trdDT_ = ql.Settings.instance().evaluationDate        
      self.matYR_ = dcA365.yearFraction(self.trdDT_, matDT)
      # ペイオフ
      self.pC_    = payOffObj.optionType()
      self.stkRT_ = payOffObj.strike()
      # 満期日DF、カーブオブジェクト
      self.matDF_ = rfOBJ.discount(matDT)
      self.rfOBJ_ = rfOBJ
      # ボラ、原資産価格
      self.volRT_ = volRT
      self.futRT_ = futRT

    # SD: 標準偏差関数
    def SD(self, volRT = None, matYR=None): 
        volRT = volRT or self.volRT_ ; matYR = matYR or self.matYR_
        return volRT*np.sqrt(matYR)
    # dd: d1関数
    def dd(self, futRT = None, volRT = None, matYR = None): 
        futRT = futRT or self.futRT_ ; volRT = volRT or self.volRT_
        matYR = matYR or self.matYR_
        return self.pC_*(futRT - self.stkRT_)/self.SD(volRT, matYR)
    # npvの計算  (関数内関数 : クロージャー)
    def npv(self, futRT = None, volRT = None, matYR = None):
        futRT = futRT or self.futRT_; volRT = volRT or self.volRT_
        matYR = matYR or self.matYR_
        matDF = self.matDF_ if matYR == self.matYR_ \
                            else self.rfOBJ_.discount(matYR*360/365)        
        d1 = self.dd(futRT, volRT, matYR) 
        return matDF*self.SD(volRT,matYR)*(d1*norm.cdf(d1) + norm.pdf(d1))