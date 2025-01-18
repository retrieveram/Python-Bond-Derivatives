import xlwings as xw ; from myABBR import * ; import myUtil as mu

@xw.func
def bsOption(pC, tradeDT, matDT, spotPRC, strkPRC,
             volRT=0.01, rfRT=0.001, npvB=0.0, Greek='NPV'):
    ''' pC: ql.Option.Call=1, Put=-1 '''
    # 初期値 (xlwingsの為、pCを整数とした)
    tradeDT,          matDT,      pC                       =\
    dDT(tradeDT), dDT(matDT), int(pC)      ; setEvDT(tradeDT)
    # 3つのハンドル, 確率過程, エンジン
    spotHDL = mu.sqHDL  (spotPRC) 
    _,rfHDL = mu.ffTSH  (tradeDT,  rfRT)
    volHDL  = mu.bVolTSH(tradeDT, volRT)
    bkPROC  = ql.BlackProcess(spotHDL, rfHDL, volHDL)
    anaENG  = ql.AnalyticEuropeanEngine(bkPROC)
    # オプション
    optOBJ  = ql.VanillaOption(ql.PlainVanillaPayoff(pC, strkPRC), 
                               ql.EuropeanExercise(matDT)         )
    optOBJ.setPricingEngine(anaENG)
    #NPV初期値(npv Begin)指定でvol計算へ
    if npvB == 0.0: npvB = optOBJ.NPV()  
    # 計算
    greeks = {"NPV": optOBJ.NPV(), "delta": optOBJ.delta(), "gamma": optOBJ.gamma(),
              "vega": optOBJ.vega(),"theta": optOBJ.thetaPerDay(),
              "vol": optOBJ.impliedVolatility(npvB, bkPROC)}
    return greeks[Greek]