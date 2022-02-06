#%%

import yfinance as yf

SPY = yf.download('SPY', start='2020-01-01') ### 미국주식
EFA = yf.download('EFA', start='2020-01-01') ### 미국 외 선진국주식
BIL = yf.download('BIL', start='2020-01-01') ### 미국 초단기채권
EEM = yf.download('EEM', start='2020-01-01') ### 신흥국주식
AGG = yf.download('AGG', start='2020-01-01') ### 미국채권
LQD = yf.download('LQD', start='2020-01-01') ### 미국회사채
IEF = yf.download('IEF', start='2020-01-01') ### 미국중기채
SHY = yf.download('SHY', start='2020-01-01') ### 미국단기국채

#%%
import pandas as pd

SPY = pd.DataFrame(SPY)
EFA = pd.DataFrame(EFA)
BIL = pd.DataFrame(BIL)
EEM = pd.DataFrame(EEM)
AGG = pd.DataFrame(AGG)
LQD = pd.DataFrame(LQD)
IEF = pd.DataFrame(IEF)
SHY = pd.DataFrame(SHY)
#%%
###################### 시간 데이터
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

today = date(2022, 1, 31)
ago_12m = today - relativedelta(years=1)
ago_6m = today - relativedelta(months=6)
ago_3m = today - relativedelta(months=3)
ago_1m = today - relativedelta(months=1)

today = today.isoformat()
ago_12m = ago_12m.isoformat()
ago_6m = ago_6m.isoformat()
ago_3m = ago_3m.isoformat()
ago_1m = ago_1m.isoformat()

time = [today, ago_12m, ago_6m, ago_3m, ago_1m]

for k in range(100):
    cnt = 0
    for i in range(len(time)):
        try:
            SPY.loc[time[i], 'Adj Close'] ### 그 날에 데이터가 있는지 확인
            cnt += 1
        except:    
            time[i] = date.fromisoformat(time[i])
            time[i] = (time[i] - relativedelta(days=1)).isoformat() ### 없으면 하루 빼기

    if cnt == 3: ### 모든 날에 데이터가 있으면 합격
        break
        
#print(time)
today, ago_12m, ago_6m, ago_3m, ago_1m = time
#print(today, ago_12m, ago_6m, ago_3m, ago_1m)

#%%
type(SPY.loc['2021-01-31', 'Adj Close'])
#%%
##########################12개월수익률
profit_SPY = (float(SPY.loc[today, 'Adj Close']) - float(SPY.loc[ago_12m, 'Adj Close'])) / float(SPY.loc[today, 'Adj Close'])
profit_BIL = (float(BIL.loc[today, 'Adj Close']) - float(BIL.loc[ago_12m, 'Adj Close'])) / float(BIL.loc[today, 'Adj Close'])
profit_EFA = (float(EFA.loc[today, 'Adj Close']) - float(EFA.loc[ago_12m, 'Adj Close'])) / float(EFA.loc[today, 'Adj Close'])

profit_12month = {'SPY':profit_SPY,
                  'BIL':profit_BIL,
                  'EFA':profit_EFA}

profit_12month

#%%
###########################이동평균
import numpy as np
import FinanceDataReader as fdr

price_SPY = SPY.loc[today, 'Adj Close']
MA200_SPY = np.mean(SPY['Adj Close'][-200:])

unemployment_rate = fdr.DataReader('unrate', start='2019', data_source='fred')
unrate_today = unemployment_rate['UNRATE'][-1]
unrate_12m = np.mean(unemployment_rate['UNRATE'][-12:])

#%%
#############################모멘텀스코어
# 공격형 자산: SPY, EFA, EEM ,AGG
# 안전자산: LQD, IEF, 미국단기국채SHY
profit = ['1m', '3m', '6m', '12m', 'mtm score']
assets = ['SPY', 'EFA', 'EEM', 'AGG', 'LQD', 'IEF', 'SHY']
asset = [SPY, EFA, EEM, AGG, LQD, IEF, SHY]
table = []
for item in asset:
    list_asset = [(float(item.loc[today, 'Adj Close']) - float(item.loc[ago_1m, 'Adj Close'])) / float(item.loc[today, 'Adj Close']),
                (float(item.loc[today, 'Adj Close']) - float(item.loc[ago_3m, 'Adj Close'])) / float(item.loc[today, 'Adj Close']),
                (float(item.loc[today, 'Adj Close']) - float(item.loc[ago_6m, 'Adj Close'])) / float(item.loc[today, 'Adj Close']),
                (float(item.loc[today, 'Adj Close']) - float(item.loc[ago_12m, 'Adj Close'])) / float(item.loc[today, 'Adj Close'])]
    mtm_asset = 12 * list_asset[0] + 4 * list_asset[1] + 2 * list_asset[2] + 1 * list_asset[3]
    list_asset.append(mtm_asset)
    table.append(list_asset)

vaa_table = pd.DataFrame(table, columns=profit, index=assets).T

# %%
########## 오리지널 듀얼 모멘텀 ##############################################

# 매수: 
# 1. 매월 말 SPY, EFA, BIL의 최근 12개월 수익률을 계산
# 2. SPY 수익률이 BIL보다 높으면 SPY 또는 EFA 중 최근 12개월 수익률이 더 높은 ETF에 투자
# 3. SPY의 수익률이 BIL보다 낮으면 AGG에 투자
# 매도: 월 1회 리밸런싱

if profit_SPY > profit_BIL:
    for item in profit_12month.keys():
        if profit_12month[item] == max(profit_SPY, profit_EFA):
            ans_Dual = item
            break
ans_Dual

# %%
############# LAA ##########################################################

# 고정자산: 미국 대형가치주 IWD, GLD IEF 
# 타이밍자산: QQQ SHY

# 매수: 
# 자산의 25%씩을 IWD, GLD, IEF에 투자 및 보유
# 나머지 25%는 나스닥 OR 미국단기국채에 투자
# - 미국 S&P 500 지수 가격이 200일 이동평균보다 낮고 미국 실업률이 12개월 이동평균보다 높은 경우 미국 단기국채에 투자
# - 그렇지 않을 경우 나스닥에 투자
# 매도:
# 고정자산: 연 1회 리밸런싱
# 타이밍자산: 월1회 리밸런싱

if (price_SPY < MA200_SPY) & (unrate_today > unrate_12m):
    ans_LAA = 'SHY'
else:
    ans_LAA = 'QQQ'
ans_LAA
# %%
############### VAA Aggressive #############################################

# 공격형 자산: SPY, EFA, EEM ,AGG
# 안전자산: LQD, IEF, 미국단기국채SHY

# 매수:
# 1. 매월 말 공격형 자산, 안전자산의 모멘텀 스코어 계산
# 2. 각 자산의 모멘텀 스코어 계산: (12X1개월수익률)+(4X3개월수익률)+(2X6개월수익률)+(1X12개월수익률)
# 3. 공격형자산 4개 모두 모멘텀스코어 0 이상일경우 전체를 가장 높은 공격형자산에 투자
# 4. 공격형자산 4개 중 한개라도 모멘텀스코어가 0 이하일 경우 포트 전체를 가장 모멘텀스코어 높은 안전자산에 투자
# 매도: 월1회 리밸런싱

if (vaa_table.loc['mtm score', 'SPY'] > 0) & (vaa_table.loc['mtm score', 'EFA'] > 0) & \
    (vaa_table.loc['mtm score', 'EEM'] > 0) & (vaa_table.loc['mtm score', 'AGG'] > 0):
    for item in vaa_table.keys():
        if vaa_table[item]['mtm score'] == max(vaa_table.loc['mtm score', 'SPY'], vaa_table.loc['mtm score', 'EFA'], 
                                               vaa_table.loc['mtm score', 'EEM'], vaa_table.loc['mtm score', 'AGG']):
            ans_vaa = item
            break
else:
    for item in vaa_table.keys():
        if vaa_table[item]['mtm score'] == max(vaa_table.loc['mtm score', 'LQD'], vaa_table.loc['mtm score', 'IEF'], 
                                               vaa_table.loc['mtm score', 'SHY']):
            ans_vaa = item
            break
ans_vaa 


# %%

# %%
# %%
