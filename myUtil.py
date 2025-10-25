from myABBR import *
from scipy.stats import norm
  
##### ショートカット #####
# シンプルクォート
def sqHDL(xx):   
  '''sqHDL(xx)=ql.QuoteHandle(ql.SimpleQuote(xx))''' 
  return ql.QuoteHandle(ql.SimpleQuote(xx))

# メイククォート (たぶん、シンプルクォートと同じ)
def mqHDL(xx):   
  '''mqHDL(xx)=ql.makeQuoteHandle(xx)''' 
  return ql.makeQuoteHandle(xx)

# フラットフォワード ** OBJとTSHの2つを戻す点に注意  **
def ffTSH(settleDT, rate, dc=dcA365, cmpd=2, freq=1):   
  '''ffTSH(settleDT,rate,dc=dcA365,cmpd=2,freq=1) 
                                    = ffCrvOBJ,ql.YTS(ql.FlatForward(...))
     cmpd=2:Continuous, 1:Compounded freq=1:Annual 2:Semiannual''' 
  ffCrvOBJ = ql.FlatForward(settleDT, rate, dc, cmpd, freq)
  ffCrvOBJ.enableExtrapolation()
  return (ffCrvOBJ, ql.YieldTermStructureHandle(ffCrvOBJ))

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
    for knd, tnr, rt in crvDATA:
        if knd == 'depo':
            if ql.Period(tnr).length() == 1:
                cHelper.append(ql.DepositRateHelper(sqHDL(rt/100),sofrIX)) 
        if knd == 'swap': cHelper.append(
            ql.OISRateHelper(Tp2, ql.Period(tnr),sqHDL(rt/100),sofrIX))
        sfParRT.append(rt/100)                             # パーレート用リスト
    sfCrvOBJ = ql.PiecewiseLogLinearDiscount(Tp0, calUSs, cHelper, dcA360)
    sfCrvHDL.linkTo(sfCrvOBJ) ; sfCrvOBJ.enableExtrapolation()
    return [sofrIX, sfCrvOBJ, sfCrvHDL, sfParRT]      # 4つのオブジェクトを戻す
  
# TONAカーブ
def makeTonaCurve(crvDATA):
    '''makeTonaCurve(crvDATA)->[tonaIX,tnCrvOBJ,tnCrvHDL,tnParRT]'''
  # 1.指標金利オブジェクト
    tnCrvHDL = ql.RelinkableYieldTermStructureHandle()  
    tonaIX = ql.OvernightIndex('TONA', Tp0,   jpyFX, calJP, dcA365, tnCrvHDL)
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
    return [tonaIX, tnCrvOBJ, tnCrvHDL, tnParRT]        # 4つのオブジェクトを戻す    
  
# TIBORカーブ
def makeTiborCurve(crvDATA):
    '''makeTiborCurve(crvDATA)->[tbrIX,tbCrvOBJ,tbCrvHDL,tbParRT]'''
  # 1.指標金利オブジェクト
    tbCrvHDL = ql.RelinkableYieldTermStructureHandle() 
    tbrIX    = ql.Tibor(pdFreqSA, tbCrvHDL)
  # 2. HelperとTiborカーブオブジェクト
    cHelper, tbParRT = [], []
    for knd, tnr, rt in crvDATA:
       if knd == 'depo': cHelper.append(ql.DepositRateHelper(sqHDL(rt/100),tbrIX)) 
       if knd == 'swap': cHelper.append(ql.SwapRateHelper(   sqHDL(rt/100),
                                     pD(tnr), calJP, freqSA, mFLLW, dcA365, tbrIX))
       tbParRT.append(rt/100)                            # パーレート用リスト
    tbCrvOBJ = ql.PiecewiseLogLinearDiscount(Tp2, calJP, cHelper, dcA365)
    tbCrvHDL.linkTo(tbCrvOBJ) ; tbCrvOBJ.enableExtrapolation()
    return [tbrIX, tbCrvOBJ, tbCrvHDL, tbParRT]  # 4つのオブジェクトを戻す  
  
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
                        dfSWP.accruStart[id],dfSWP.accruEnd[id], dcA365, cmpdSPL).rate()
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