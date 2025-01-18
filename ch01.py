from myABBR import * ; import myUtil as mu
import xlwings as xw
@xw.func

def tiborDF(r3m, r6m, r12m, tgtDT):
    tradeDT  = jDT(2022,8,1) ;     setEvDT(tradeDT)
    settleDT = calJP.advance(tradeDT, Tp2, DD)
    tbr3m    = ql.Tibor(pdFreqQ )
    tbr6m    = ql.Tibor(pdFreqSA)
    tbr12m   = ql.Tibor(pdFreqA )

    rate3mHDL  = mu.sqHDL( r3m)
    rate6mHDL  = mu.sqHDL( r6m)
    rate12mHDL = mu.sqHDL(r12m)        

    helper3m  = ql.DepositRateHelper(rate3mHDL,  tbr3m)
    helper6m  = ql.DepositRateHelper(rate6mHDL,  tbr6m) 
    helper12m = ql.DepositRateHelper(rate12mHDL,tbr12m)
    helpers   = [helper3m, helper6m, helper12m ]

    curveOBJ = ql.PiecewiseLogLinearDiscount(settleDT, helpers, dcA365)
    curveOBJ.enableExtrapolation()
    return curveOBJ.discount( dDT(tgtDT) ) 

@xw.func
@xw.arg('data', ndim=1)
def tiborDF2(data):
    r3m, r6m, r12m, tgtDT = data
    tradeDT  = jDT(2022,8,1) ;  setEvDT(tradeDT)
    settleDT = calJP.advance(tradeDT, Tp2, DD)
    tbr3m    = ql.Tibor(pdFreqQ )
    tbr6m    = ql.Tibor(pdFreqSA)
    tbr12m   = ql.Tibor(pdFreqA )

    rate3mHDL  = mu.sqHDL( r3m)
    rate6mHDL  = mu.sqHDL( r6m)
    rate12mHDL = mu.sqHDL(r12m)        

    helper3m  = ql.DepositRateHelper(rate3mHDL,  tbr3m)
    helper6m  = ql.DepositRateHelper(rate6mHDL,  tbr6m) 
    helper12m = ql.DepositRateHelper(rate12mHDL,tbr12m)
    helpers   = [helper3m, helper6m, helper12m ]

    curveOBJ = ql.PiecewiseLogLinearDiscount(settleDT, helpers, dcA365)
    curveOBJ.enableExtrapolation()
    return curveOBJ.discount( dDT(tgtDT) ) 