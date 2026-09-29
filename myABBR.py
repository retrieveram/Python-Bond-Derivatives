#---- A. ライブラリーインポート ----
import QuantLib          as ql
import pandas            as pd
import numpy             as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import warnings          #警告の非表示用(pandas ilocで止める)
from functools   import singledispatch   #関数オーバーロード用
import datetime as dt
from scipy.stats import norm

#---- B. matplotlib初期設定  ----
# 日本語フォントとサイズ、グラフサイズ
# xNum:x軸の表示個数  xRot:x軸表示角度 yPct:y軸 %  yFlt:y軸少数桁数 gdShow:グリッドshow
plt.rcParams.update({"font.family"   :"MS Gothic",
                     "font.size"     :9,
                     "figure.figsize":[4.5,2.5]})
def xNum(ax, num=10):                                  # x軸の表示項目数を指定
  for aa in np.atleast_1d(ax): aa.xaxis.set_major_locator(mtick.MaxNLocator(num))
def xRot(ax, angle=45):                                # x軸の表示項目の角度を指定
  for aa in np.atleast_1d(ax): aa.tick_params(axis='x', labelrotation=angle)
def yPct(ax, decimals=3, ymax=1):                      # yPct:y軸を%表示 yFlt:少数桁数を指定
  ax.yaxis.set_major_formatter(mtick.PercentFormatter(ymax,decimals))
def yFlt(ax, decimals=2): ax.yaxis.set_major_formatter(
                    mtick.StrMethodFormatter(f'{{x:,.{decimals}f}}'))
def gdShow(ax,linewidth=1):
  for aa in np.atleast_1d(ax): aa.grid(linestyle='--',linewidth=1)
  plt.tight_layout(); plt.show()
def lgD(ax):                                          # labelの指定の有無をチェック
  for aa in np.atleast_1d(ax):
    hdl,_ = aa.get_legend_handles_labels()
    if hdl: aa.legend()
#---- C. numpy初期設定 5桁表示と配列短縮形, 切捨て ----
np.set_printoptions(precision=5,suppress=True)
def nSetP(dgt=5):                     # %5桁表示設定
  fmt = '{:.' + str(dgt) + '%}'
  np.set_printoptions(formatter={'float':fmt.format})
def nSetF(dgt=5):                     # float5桁表示設定
  np.set_printoptions(precision=dgt,suppress=True)
def nA(LIST):        return np.array(LIST)
def rD(xx,digits=0): return np.floor(xx * 10**digits)/10**digits #切捨て
def rU(xx,digits=0): return np.ceil (xx * 10**digits)/10**digits #切上げ

#---- D. pandas 表示設定, スタイル書式用変数, df表示, 日付列変換 ----
# pd.set_option("display.precision",10)
def colMn(): pd.set_option('display.max_columns', None)         # 列数の上限なし
def colM (): pd.set_option('display.max_columns')               # 元の設定に戻す
def dspW (n=None): pd.set_option('display.width', n)            # 表示幅をn文字数
colMn(); dspW(95)                                               # 初期設定
fmS = {'amount' :'{:,.2f}',  'atmFWD':'{:.6%}' ,  'coupon':'{:.6%}' ,
       'days'   :'{:.0f}' ,  'DF'    :'{:.8f}' ,  'fwdRT' :'{:.6%}' ,
       'nominal':'{:,.2f}',  'NPV'   :'{:,.2f}',  'matYR' :'{:,.4f}',
       'parRT'  :'{:.6%}' ,  'rate'  :'{:.6%}' ,  'rfrDF' :'{:.8f}' ,
       'shftRT' :'{:.6%}' ,  'spread':'{:.3%}' ,  'zeroRT':'{:.6%}' ,}
fmB = {'accruAMT':'{:,.4f}', 'amount'  :'{:,.4f}', 'BPV'  :'{:.4f}',
       'CF'      :'{:.5f}' , 'cleanPRC':'{:.4f}' ,'coupon':'{:.4%}',
       'dirtyPRC':'{:.4f}' , 'gBASIS'  :'{:.4f}' , 'yield':'{:.4f}', }
fmO = {'Amount' :'{:,.2f}','Base NPV':'{:,.2f}','NPV':'{:,.2f}',
       'Coupon':'{:.6%}','Delta': '{:,.2f}',
       'DiscountFactor':'{:.8f}','Gamma': '{:,.2f}', 'val': '{:,.2f}',
       'MaturityTime':'{:.2f}','Notional':'{:,.2f}',
       'PresentValue':'{:,.2f}','ShiftSize_1':'{:.4%}' }  # for ORE
fmE = {'EPE' :'{:,.2f}','ENE':'{:,.2f}','AllocatedEPE':'{:,.2f}',
       'AllocatedENE' :'{:,.2f}','PFE':'{:,.2f}','BaselEE':'{:,.2f}',
       'BaselEEE':'{:,.2f}','TimeWeightedBaselEPE': '{:,.2f}',
       'TimeWeightedBaselEEPE': '{:,.2f}'}  # for Exposure
fmX = {'CVA':'{:,.2f}','DVA':'{:,.2f}','FBA':'{:,.2f}','FCA':'{:,.2f}',
       'FBAexOwnSP':'{:,.2f}','FCAexOwnSP':'{:,.2f}','FBAexAllSP':'{:,.2f}',
       'FCAexAllSP':'{:,.2f}','COLVA':'{:,.2f}','MVA':'{:,.2f}',
       'OurKVACCR':'{:,.2f}','TheirKVACCR':'{:,.2f}','OurKVACVA':'{:,.2f}',
       'TheirKVACVA':'{:,.2f}','CollateralFloor':'{:,.2f}',
       'AllocatedCVA':'{:,.2f}','AllocatedDVA':'{:,.2f}',
       'BaselEPE':'{:,.2f}','BaselEEPE':'{:,.2f}'}  # for XVA
oeSENSI = ['TradeId','Factor_1','Currency','Base NPV','ShiftSize_1',
           'Delta','Gamma']
oeCF    = ['TradeId','LegNo','PayDate','AccrualStartDate',
           'AccrualEndDate','Coupon','Amount', 'DiscountFactor']
fmtSCF, fmtFUT = fmS, fmB                                # for old vari.
def dfDSP(df, n=5, fm=fmS):    # n: numbers of line, fm: format vari.
  nRow = min(n, (len(df)+1)//2 )
  tmp  = pd.concat([df.head(nRow),df.tail(nRow)])
  sty = tmp.loc[~tmp.index.duplicated(keep="first")].style
  sty  = sty.format(fm); display(sty)
def dfSTL(dfxx, fm=fmS): display(dfxx.style.format(fm))
def dfSTLT(dfxx, fm=fmS):                          # 転置したdfのスタイル表示
	styOB = dfxx.T.style
	for col, fmt in fm.items():
		styOB = styOB.format(fmt, subset=pd.IndexSlice[col, :])
	display( styOB )
def pdDT (dateCOL): return pd.to_datetime(dateCOL)
def isoDT(dateCOL):                                              # ql日付からiso日付へ
      return dateCOL.map(lambda x: x.ISO() if not pd.isna(x) else x)
def qlDT(dateCOL) :                                              # iso日付からql日付へ
      return dateCOL.map(lambda x: iDT(x)  if not pd.isna(x) else x)

#---- E. 日付関連メソッドの短縮形 ----
# Days, Weeks, Months, Years
DD = ql.Days; WW = ql.Weeks; MM = ql.Months; YY = ql.Years
# euro日付
def eDT(dd,mm,yyyy): return ql.Date(dd,mm,yyyy)
# japan日付
def jDT(yyyy,mm,dd): return ql.Date(dd,mm,yyyy)
# us日付
def uDT(mm,dd,yyyy): return ql.Date(dd,mm,yyyy)
# datetimeクラスからQL Date
def dDT(dateTIME):   return ql.Date().from_date(dateTIME)
# iso日付
def iDT (isoDT):      return ql.Date(isoDT, '%Y-%m-%d')
def iDTd(isoDT):      return dt.fromisoformat(isoDT)
# 曜日 day of week
def dWK(Date): return Date.to_date().strftime('%a')
# dcXX.yearFraction(base,tgt)
def yrF(dcOBJ,baseDT,tgtDT) : return dcOBJ.yearFraction(baseDT,tgtDT)
# xxx.advance( , , DD)等
def adD(cal,dt,nn) : return cal.advance(dt, nn, DD)
def adW(cal,dt,nn) : return cal.advance(dt, nn, WW)
def adM(cal,dt,nn) : return cal.advance(dt, nn, MM)
def adY(cal,dt,nn) : return cal.advance(dt, nn, YY)
# 月初と月末の日付、月の日数
def bDTmm(d) :       return ql.Date(1, d.month(), d.year())
def eDTmm(d) :       return d.endOfMonth(d)
def dsMM(d)  :       return ql.Date.endOfMonth(d).dayOfMonth()
# SettingクラスevaluationDate設定、取得
def setEvDT(evaluationDT):
  ql.Settings.instance().evaluationDate = evaluationDT
def getEvDT():       return ql.Settings.instance().evaluationDate

# Period 3種類の短縮形 (2番目はタプルが引数)
@singledispatch
def pD(pdSTR: str): return ql.Period(pdSTR)  # Period('3M')
@pD.register(tuple)
def _(nnUNT):       return ql.Period(*nnUNT) # Period((3,MM))
@pD.register(int)
def _(FRQ):         return ql.Period(FRQ)    # Period(freqQ)


#---- F. 短縮形リスト ----
# Calendar
calJP   =  ql.Japan()
calEU   =  ql.TARGET()
calUSf  =  ql.UnitedStates(ql.UnitedStates.FederalReserve)
calUSg  =  ql.UnitedStates(ql.UnitedStates.GovernmentBond)
calUSs  =  ql.UnitedStates(ql.UnitedStates.SOFR)
calWK   =  ql.WeekendsOnly()
calNL   =  ql.NullCalendar()
calUJ   =  ql.JointCalendar(calUSf, calJP)
# DayCounter
dcA365  =  ql.Actual365Fixed()
dcA365n =  ql.Actual365Fixed(ql.Actual365Fixed.NoLeap)
dcA360  =  ql.Actual360()       # includeLastDay=false
dcA360t =  ql.Actual360(True)   # for CDS
dc30    =  ql.Thirty360(ql.Thirty360.BondBasis)
dc30e   =  ql.Thirty360(ql.Thirty360.European)
dcAA    =  ql.ActualActual(ql.ActualActual.ISDA)
dcAAb   =  ql.ActualActual(ql.ActualActual.Bond)
# T + Business days (settle days)
Tp0     =  0
Tp1     =  1
Tp2     =  2
Tp3     =  3
# freqency
frqA   =  ql.Annual                  # 1
frqSA  =  ql.Semiannual              # 2
frqQ   =  ql.Quarterly               # 4
frqM   =  ql.Monthly                 # 12
frqD   =  ql.Daily                   # 365
frq0   =  ql.NoFrequency             # 0  for ql.Continuous
# OLD-freqency
freqA   =  ql.Annual                  # 1
freqSA  =  ql.Semiannual              # 2
freqQ   =  ql.Quarterly               # 4
freqM   =  ql.Monthly                 # 12
freqD   =  ql.Daily                   # 365
# tenor (period version for freq)
pDfrqA =  ql.Period(ql.Annual)       # 1Y
pDfrqSA=  ql.Period(ql.Semiannual)   # 6M
pDfrqQ =  ql.Period(ql.Quarterly)    # 3M
pDfrqM =  ql.Period(ql.Monthly)      # 1M
pDfrqD =  ql.Period(ql.Daily)        # 1D
# OLD-tenor
pdFreqA =  ql.Period(ql.Annual)       # 1Y
pdFreqSA=  ql.Period(ql.Semiannual)   # 6M
pdFreqQ =  ql.Period(ql.Quarterly)    # 3M
pdFreqM =  ql.Period(ql.Monthly)      # 1M
pdFreqD =  ql.Period(ql.Daily)        # 1D
# convension
mFLLW   =  ql.ModifiedFollowing
FLLW    =  ql.Following
unADJ   =  ql.Unadjusted
# date generation
dtGENb  =  ql.DateGeneration.Backward
dtGENf  =  ql.DateGeneration.Forward
dtGEN20 =  ql.DateGeneration.TwentiethIMM
dtGENc  =  ql.DateGeneration.CDS
dtGEN15 =  ql.DateGeneration.CDS2015
# end of month
EoMf    =  False
EoMt    =  True
# compound
CMP =  ql.Compounded
CNT =  ql.Continuous
SPL =  ql.Simple
# OLD-compound
cmpdCMP =  ql.Compounded
cmpdCNT =  ql.Continuous
cmpdSPL =  ql.Simple

# swap: pay/recieve, option: put/call
swPAY   = ql.Swap.Payer       #  1
swRCV   = ql.Swap.Receiver    # -1
opCL    = ql.Option.Call      #  1
opPT    = ql.Option.Put       # -1
cpnRT0  = 0.0
spdRT0  = 0.0
gr1     = 1.0              # gearing
# currency
jpyCY   =  ql.JPYCurrency()
usdCY   =  ql.USDCurrency()
eurCY   =  ql.EURCurrency()
# CDS : recovery rate / coupon
rcvRTz  = 0.0     # zero
rcvRTj  = 0.35    # Japan
rcvRTu  = 0.40    # US
rcvRTs  = 0.20    # subordinate
cpn025  = 0.0025
cpn100  = 0.01
cpn500  = 0.05
bP      = ql.Protection.Buyer  # 0
sP      = ql.Protection.Seller # 1
# Lag
lag0d    = 0
lag1d    = 1
lag2d    = 2
lag3M    = ql.Period('3M')
lag0M    = ql.Period('0M')

# bond, CPI, クリーン価格等
parPR    = 100.0
parAMT   = 100.0
cpiLNR   = ql.CPI.Linear
cpiFLT   = ql.CPI.Flat
ds9      = 9            # shift days for JGBI
gwOLY    = False
reviseF  = False
jpRegion = ql.CustomRegion("Japan", "JP")
usRegion = ql.CustomRegion("USA",   "US")
def cP(prc):       return ql.BondPrice(prc, ql.BondPrice.Clean)
def dP(prc):       return ql.BondPrice(prc, ql.BondPrice.Dirty)

# percent and basis points
pct     =  1e-2
bps     =  1e-4

# シンプルクォート、シンプルキャッシュフロー
def sQ(xx):        return ql.SimpleQuote(xx)
def sQH(xx):       return ql.QuoteHandle(sQ(xx))
def sCF(amt,date): return ql.SimpleCashFlow(amt, date)

# 乱数object
def uniRNG(nSeed):
   return ql.UniformRandomGenerator(nSeed)
def uniSeqRNG(nSeed, nRnd):
   return ql.UniformRandomSequenceGenerator(nRnd, uniRNG(nSeed))
def gsSeqRNG(nSeed, nRnd):
   return ql.GaussianRandomSequenceGenerator(uniSeqRNG(nSeed,nRnd))
# エンジン セット
def setPE(obj,eng): return obj.setPricingEngine(eng)