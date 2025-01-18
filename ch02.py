import xlwings as xw ; from myABBR import * ; import myUtil as mu

@xw.func 
@xw.arg('dateINF', ndim=1)
@xw.arg('legINF', ndim=1)
@xw.arg('crvDATA', ndim=2)
@xw.ret(index=False, header=True, expand='table')

def tiborSWAP(dateINF,legINF,crvDATA,cftable=-1): # cftable=> 固定表:0, 変動表:1
    # 0.引数の処理
    tradeDT, effDT,  matDT                  = dateINF
    payRcv,  ntlAMT, cpnRT, sprdRT, fixedIX = legINF

    tradeDT,          effDT,      matDT,      payRcv   =\
    dDT(tradeDT), dDT(effDT), dDT(matDT), int(payRcv)

    settleDT = calJP.advance(tradeDT,Tp2,DD) ; setEvDT(tradeDT)
    # 1.カーブ作成
    tbrIX, tbCrvOBJ, tbCrvHDL, tbParRATE = mu.makeTiborCurve(crvDATA)
    # 2.スケジュールオブジェクト 
    fixSCD = ql.Schedule(effDT, matDT, pdFreqSA, calJP, mFLLW, mFLLW, dtGENb, EoMf)
    # 3.スワップオブジェクト
    swapOBJ = ql.VanillaSwap(payRcv,ntlAMT,fixSCD,cpnRT,       dcA365,
                                        fixSCD,tbrIX,sprdRT,dcA365)
    swapENG = ql.DiscountingSwapEngine(tbCrvHDL) ; swapOBJ.setPricingEngine(swapENG)
    # 4.fixed指標金利の設定
    prevPayDT = settleDT if swapOBJ.floatingSchedule().startDate() >= settleDT \
                       else swapOBJ.floatingSchedule().previousDate(settleDT)
    fixedDT = calJP.advance(prevPayDT,-Tp2,DD)
    tbrIX.clearFixings() ;  tbrIX.addFixing(fixedDT,fixedIX)
    # 5.Retrun   ( cftable=> 固定表:0, 変動表:1 評価:初期値 )
    if cftable == 1 :                                      #1:変動レグキャッシュフロー
        df = mu.swapCashFlow(swapOBJ, tbCrvOBJ, 1)
    elif cftable == 0 :                                    #0:固定レグキャッシュフロー
        df = mu.swapCashFlow(swapOBJ, tbCrvOBJ, 0)
    else:                                                  #スワップ評価
        df =pd.DataFrame([  
        ['固定レグ時価'    ,swapOBJ.legNPV(0)],   ['変動レグ時価',swapOBJ.legNPV(1)],
        ['スワップ時価 NPV',swapOBJ.NPV()],       ['フェアレート',swapOBJ.fairRate()],
        ['フェアスプレッド',swapOBJ.fairSpread()]         ], columns=['計算結果', ''])
    return df