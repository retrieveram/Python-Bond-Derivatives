#---- A. ライブラリーインポート ----
import QuantLib          as ql
import datetime          as dt 
import pandas            as pd
import numpy             as np 
import matplotlib.pyplot as plt 
import matplotlib.ticker as mtick
import warnings          #警告の非表示用(pandas ilocで止める)
from functools import singledispatch   #関数オーバーロード用

#---- B. matplotlib初期設定  ----
#     日本語フォントとサイズ、グラフサイズ
plt.rcParams.update({"font.family"   :"MS Gothic",
                     "font.size"     :9,
                     "figure.figsize":[4.5,2.5]})

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

#---- D. pandasスタイル書式用 辞書型変数 ----
fmtSCF = {'amount':'{:,.2f}','atmFWD':'{:.6%}','coupon':'{:.6%}',
          'days':'{:.0f}',   'DF':'{:.8f}',    'nominal':'{:,.2f}',
          'NPV':'{:,.2f}',   'matYR':'{:,.4f}','parRT':'{:.6%}',
          'rate':'{:.6%}',   'shftRT':'{:.6%}','spread':'{:.3%}',
          'zeroRT':'{:.6%}'}
fmtFUT = {'accruAMT':'{:,.4f}', 'amount':'{:,.4f}',  'BPV':'{:.4f}',
          'CF':'{:.5f}',        'cleanPRC':'{:.4f}', 'coupon':'{:.4%}',
          'dirtyPRC':'{:.4f}',  'gBASIS':'{:.4f}',   'yield':'{:.4f}' }

#---- E. 日付関連メソッドの短縮形 ----
# Days, Weeks, Months, Years
DD = ql.Days ;  WW = ql.Weeks ;  MM = ql.Months ;  YY = ql.Years
# euro日付
def eDT(dd,mm,yyyy): return ql.Date(dd,mm,yyyy)
# japan日付
def jDT(yyyy,mm,dd): return ql.Date(dd,mm,yyyy)
# us日付
def uDT(mm,dd,yyyy): return ql.Date(dd,mm,yyyy)
# datetimeクラスからQL Date
def dDT(dateTIME):   return ql.Date().from_date(dateTIME)
# iso日付
def iDT(isoDT):      return ql.Date(isoDT, '%Y-%m-%d')
# 曜日
def dayOfWeek(Date): return Date.to_date().strftime('%a')
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
# pay/recieve, put/call
swPAY   = ql.Swap.Payer
swRCV   = ql.Swap.Receiver

# currency
jpyFX   =  ql.JPYCurrency()
usdFX   =  ql.USDCurrency()
eurFX   =  ql.EURCurrency()
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
# bond, CPI, クリーン価格等
parPR    = 100.0
parAMT   = 100.0
cpiLNR   = ql.CPI.Linear
cpiFLT   = ql.CPI.Flat
ds9      = 9
lag3M    = ql.Period('3M')
lag0M    = ql.Period('0M')
gwOLY    = False
reviseF  = False
jpRegion = ql.CustomRegion("Japan", "JP")
usRegion = ql.CustomRegion("USA",   "US")

def cP(prc): return ql.BondPrice(prc, ql.BondPrice.Clean)
def dP(prc): return ql.BondPrice(prc, ql.BondPrice.Dirty)
