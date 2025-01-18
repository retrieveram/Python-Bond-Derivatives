# 債券評価用xlwings
import xlwings as xw ; from myABBR import * ; import myUtil as mu
@xw.func
@xw.arg('trdDATA', ndim=1)
@xw.arg('bondDTL', ndim=1)
@xw.arg('bondCONV', ndim=1)
@xw.ret(index=False, header=True, expand='table')

def bondCALC(trdDATA, bondDTL, bondCONV):
    # 0. パラメーター編集と初期設定
    tradeDT, settDS, mktYLD       = trdDATA
    effDT, matDT, faceAMT, cpnLST = bondDTL
    calBD, cmpdBD, dcBD, freqBD, cpnCNV, matCNV, dtGenBD, EoMBD   =\
                                                     [eval(ii) for ii in bondCONV]
    tradeDT,         effDT,       matDT,    cpnLST,     settDS    =\
    dDT(tradeDT), dDT(effDT), dDT(matDT),  [cpnLST], int(settDS) 
    settleDT = calBD.advance(tradeDT, settDS, DD) ; setEvDT(tradeDT)

    # 1. スケジュール/債券オブジェクトの作成
    bondSCD = ql.Schedule(effDT,matDT,pD(freqBD),calBD,cpnCNV,matCNV,dtGenBD,EoMBD)
    bondOBJ = ql.FixedRateBond(settDS, faceAMT, bondSCD, cpnLST, dcBD)

    # 2. 利回り >> 価格計算
    preCpnDT = bondSCD.previousDate(settleDT)
    accruDS  = dcBD.dayCount(preCpnDT, settleDT)
    # bondOBJのメソッド
    accruAMT = bondOBJ.accruedAmount()
    cleanPRC = bondOBJ.cleanPrice(mktYLD, dcBD, cmpdBD, freqBD)
    dirtyPRC = bondOBJ.dirtyPrice(mktYLD, dcBD, cmpdBD, freqBD)
    dfPRC = pd.DataFrame([ 
                ['受渡日', settleDT.to_date()], ['前回利払日',preCpnDT.to_date()],
                ['経過日数', accruDS],          ['経過利息',accruAMT],
                ['---- ---- ----', ''],
                ['クリーン価格', cleanPRC],     ['利含み価格',dirtyPRC], 
                ['---- ---- ----', ''] ],  columns=['計算結果',''])   ; dfPRC
        
    # 3. リスク指標の算出
    iRateOBJ = ql.InterestRate(mktYLD, dcBD, cmpdBD, freqBD)
    MacDUR = ql.BondFunctions.duration(       bondOBJ, iRateOBJ, ql.Duration.Macaulay)
    ModDUR = ql.BondFunctions.duration(       bondOBJ, iRateOBJ)
    BPV    = ql.BondFunctions.basisPointValue(bondOBJ, iRateOBJ)
    convX  = ql.BondFunctions.convexity(      bondOBJ, iRateOBJ)
    dfRSK = pd.DataFrame([['マコーレイDur.', MacDUR],['修正Dur.', ModDUR],['BPV', BPV], 
                          ['Convexity', convX], ],            columns=['計算結果',''])
    return pd.concat([dfPRC, dfRSK], ignore_index=True)