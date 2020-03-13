#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import pandasql
import re
def req_columns_from_df1():
    #taking only required columns from the tables
    df1=pd.read_csv("../inputs/2018_20.csv")
    df1.columns=map(str.lower,df1.columns)
    df1['timestamp']= pd.to_datetime(df1['timestamp']).dt.date
    df1=df1[['symbol','series','timestamp','close','prevclose','open','high','low','close','last','tottrdqty','totaltrades']]
    #changing column names excluding special characters and extra spaces
    df1.columns=['symbol','series','timestamp','closing','prevclose','open','high','low','close','last','tottrdqty','totaltrades']
    return df1
def req_columns_from_df2():
    df2=pd.read_csv("../outputs/cor_act_with_fac.csv")
    df2.columns=map(str.lower,df2.columns)
    df2['ex-date'] = pd.to_datetime(df2['ex-date'])
    df2=df2[['symbol','series','company','purpose','ex-date','interim div','face split','bonus','final div','special div','div','fourth dist','rightscalc','first dist','capital reduction','consolidation','dist interest payment','distribution','second dist','third dist','rights','principle','return of capital']]
    df2.columns=['symbol','series','company','purpose','exdt','interimdiv','facesplit','bonus','finaldiv','specialdiv','div','fourthdist','rightscalc','firstdist','capitalred','consolidation','distintpay','dist','secdist','thirddist','rights','principle','returnofcapital']
    return df2
def nse_clean_table():
    #sub_data is nseCorporateActionsClean table
    df1=req_columns_from_df1()
    df2=req_columns_from_df2()
    sub_data = pandasql.sqldf("SELECT d2.symbol,d2.series,d2.company,d2.purpose,d2.exdt,d2.interimdiv,d2.facesplit,d2.bonus,d2.finaldiv,d2.specialdiv,d2.div,d2.fourthdist,d2.rightscalc,d2.firstdist,d2.capitalred,d2.consolidation,d2.distintpay,d2.dist,d2.secdist,d2.thirddist,d2.rights,d2.principle,d2.returnofcapital, (SELECT closing FROM df1 WHERE symbol = d2.symbol AND series = d2.series AND timestamp = d2.exdt) AS extPrice,d1.prevclose as preclose, d1.timestamp as cumDate from df2 d2 inner join df1 d1 on d2.symbol=d1.symbol and d2.series=d1.series and d1.timestamp=(SELECT MAX(timestamp) FROM df1 WHERE symbol = d2.symbol AND series = d2.series AND timestamp < d2.exdt)", locals())
    sub_data['intdivFac']=round((sub_data['preclose']-sub_data['interimdiv'])/(sub_data['preclose']),2)
    sub_data['finaldivFac']=round((sub_data['preclose']-sub_data['finaldiv'])/(sub_data['preclose']),2)
    sub_data['divFac']=round((sub_data['preclose']-sub_data['div'])/(sub_data['preclose']),2)
    sub_data['fourthdistFac']=round((sub_data['preclose']-sub_data['fourthdist'])/(sub_data['preclose']),2)
    sub_data['firstdistFac']=round((sub_data['preclose']-sub_data['firstdist'])/(sub_data['preclose']),2)
    sub_data['distintpayFac']=round((sub_data['preclose']-sub_data['distintpay'])/(sub_data['preclose']),2)
    sub_data['distFac']=round((sub_data['preclose']-sub_data['dist'])/(sub_data['preclose']),2)
    sub_data['secdistFac']=round((sub_data['preclose']-sub_data['secdist'])/(sub_data['preclose']),2)
    sub_data['thirddistFac']=round((sub_data['preclose']-sub_data['thirddist'])/(sub_data['preclose']),2)
    sub_data['rightsFac']=round(((sub_data['preclose']+sub_data['rights'])/(sub_data['rightscalc'])),2)
    sub_data['rightsFac']=round(sub_data['rightsFac']/sub_data['preclose'],2)
    sub_data['returnofcapFac']=round((sub_data['preclose']-sub_data['returnofcapital'])/(sub_data['preclose']),2)
    sub_data['principleFac']=round((sub_data['preclose']-sub_data['principle'])/(sub_data['preclose']),2)
    sub_data['factor']=round(sub_data['intdivFac']*sub_data['finaldivFac']*sub_data['divFac']*sub_data['fourthdistFac']*sub_data['firstdistFac']*sub_data['distintpayFac']*sub_data['distFac']*sub_data['secdistFac']*sub_data['thirddistFac']*sub_data['returnofcapFac']*sub_data['principleFac']*sub_data['rightsFac']*sub_data['facesplit']*sub_data['consolidation']/(sub_data['bonus']*sub_data['capitalred']),3)
    sub_data.loc[sub_data['factor']<=0,'factor']=1
    #replacing missing values with 1's
    sub_data['extPrice'].fillna(1,inplace=True)
    sub_data['preclose'].fillna(1,inplace=True)
    sub_data.to_csv('../outputs/CorpActionclean.csv')
    print('created nse corporate actions clean csv file')
    return sub_data
def nse_hist_table():
    #df3 is nsedailybhavhist table
    df3=pd.read_csv('../inputs/2018_20.csv')
    df3.columns=map(str.lower,df3.columns)
    df3['timestamp']= pd.to_datetime(df3['timestamp']).dt.date
    df3['fac']=1
    return df3
def clean():
    #data is cleaned table
    sub_data=nse_clean_table()
    df3=nse_hist_table()
    data=pandasql.sqldf("SELECT s.symbol,s.series,s.specialdiv,d3.open,d3.high,d3.low,d3.close,d3.last,d3.prevclose,d3.tottrdqty,d3.timestamp,s.factor*d3.fac as factMul from sub_data s inner join df3 d3 where s.series=d3.series and s.symbol=d3.symbol and d3.timestamp<s.exdt", locals())
    data['openAdj']=round(data['open']*data['factMul']-data['specialdiv'],2)
    data['highAdj']=round(data['high']*data['factMul']-data['specialdiv'],2)
    data['lowAdj']=round(data['low']*data['factMul']-data['specialdiv'],2)
    data['closeAdj']=round(data['close']*data['factMul']-data['specialdiv'],2)
    data['lastAdj']=round(data['last']*data['factMul']-data['specialdiv'],2)
    data['prevcloseAdj']=round(data['prevclose']*data['factMul']-data['specialdiv'],2)
    data['tottrdqtyAdj']=round(data['tottrdqty']/(data['factMul']),0)
    data=data.drop(['specialdiv'],axis=1)
    data.to_csv('../outputs/cleaned.csv')
    print('created cleaned csv file')
if __name__ == '__main__':
    clean()

    