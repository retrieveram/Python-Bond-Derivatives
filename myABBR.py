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

#---- C. numpy初期設定 5桁表示と配列短縮形 ----
np.set_printoptions(precision=5,suppress=True) 
def nSetP():                     # %5桁表示設定
  np.set_printoptions(formatter={'float':'{:.5%}'.format}) 
def nSetF():                     # float5桁表示設定
  np.set_printoptions(precision=5,suppress=True) 
def nA(LIST):        return np.array(LIST)

#---- D. pandasスタイル書式用 辞書型変数 ----
fmtSCF = {'amount':'{:,.2f}','atmFWD':'{:.6%}','coupon':'{:.6%}',
          'days':'{:.0f}',   'DF':'{:.8f}',    'nominal':'{:,.2f}',
          'NPV':'{:,.2f}',   'matYR':'{:,.4f}','parRT':'{:.6%}',
          'rate':'{:.6%}',   'shftRT':'{:.6%}','spread':'{:.3%}',
          'zeroRT':'{:.6%}'}
fmtFUT = {'BPV':'{:.4f}',   'CF':'{:.5f}',      'cleanPRC':'{:.4f}',
          'coupon':'{:.4%}','dirtyPRC':'{:.4f}','gBASIS':'{:.4f}',
          'yield':'{:.4f}', 'amount':'{:,.4f}', 'accruAMT':'{:,.4f}'}

#---- E. 日付関連メソッドの短縮形 ----
# Days, Months, Years
DD  =  ql.Days
WW  =  ql.Weeks
MM  =  ql.Months
YY  =  ql.Years
# japan日付
def jDT(yyyy,mm,dd): return ql.Date(dd,mm,yyyy)
# datetimeクラスからQL Date
def dDT(dateTIME):   return ql.Date().from_date(dateTIME)
# iso日付
def iDT(isoDT):      return ql.Date(isoDT, '%Y-%m-%d')
# 曜日
def dayOfWeek(Date): return Date.to_date().strftime('%a')
# SettingクラスevaluationDate設定
def setEvDT(evaluationDT):  
  ql.Settings.instance().evaluationDate = evaluationDT
# Period 2種類の短縮形
@singledispatch
def pD(txt: str):       return ql.Period(txt)
@pD.register                                   
def _(nn: int, yy: str):return ql.Period(nn,yy)


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
freqA   =  ql.Annual
freqSA  =  ql.Semiannual
freqQ   =  ql.Quarterly
freqD   =  ql.Daily
# tenor (period version for freq)
pdFreqA =  ql.Period(ql.Annual)
pdFreqSA=  ql.Period(ql.Semiannual)
pdFreqQ =  ql.Period(ql.Quarterly)
pdFreqD =  ql.Period(ql.Daily)
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
cmpdCMP =  ql.Compounded
cmpdCNT =  ql.Continuous
cmpdSPL =  ql.Simple
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
# others
parPR   = 100.0
parAMT  = 100.0