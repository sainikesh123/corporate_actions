#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import re
import os
import os.path
import pathlib
import logging
import config_reader
import datetime as dt
from datetime import date
from datetime import datetime, timedelta

def create_logger():
    logger = logging.getLogger(__name__)
    if not os.path.exists('../logs'):
        os.makedirs('../logs')
    dt_str = str(dt.datetime.now()).replace(' ', '_' ).replace('-','').replace(':', '').split('.')[0]
    logging.basicConfig(filename='../logs/corporate_actions'+ dt_str+'.log', filemode='a', format='%(process)d  %(asctime)s %(levelname)s %(funcName)s %(lineno)d ::: %(message)s', level=logging.INFO)
    return logger
# importing from config.properties file
def config_imports(logger):
    try:
        config = config_reader.get_config()
        return config
    except Exception as e:
        logger.exception('ERROR:: Some issue in reading the Config...check config_reader.py script in bin Folder....')
        raise e
def datafrme():
    df=pd.read_csv("../inputs/CA_LAST_24_MONTHS.csv")
    df=df.drop(['Industry','No Delivery Start Date','No Delivery End Date'],axis=1)
    return df
def splitted1():
    df=datafrme()
    #a is list of all rows of purpose column
    #a1 is the list after splitting with respect to values
    a=df['Purpose'].tolist()
    a=[row.lower().strip() for row in a]
    a1=[re.split(r'(\d*\d.?\d*)', s) for s in a]
    namva=[]
    for l in a1:
        l2=[]
        cnt=0
        for row in l:
            if re.search(r'\d+',row):
                row=row.strip('/').strip()
                l2.append(row)
                cnt+=1
            if re.search(r'[a-zA-Z]+',row) and cnt<=1:
                for ch in ['-','(purposerevised)','(daterevised)','(subdivision)','(dateandpurposerevised)','rs.','rs','-from','to','from','re',' ']:
                     if ch in row:
                        row=row.replace(ch,'').strip()
                l2.append(row)
                cnt+=1
        namva.append(l2)
    namval=[]
    for l in namva:
        if "facevaluesplit" and "rights:" not in l:
            namval.append(l[:2])
        else:
            namval.append(l)
    return namval,a1,df
    #namva is a list after removing some unwanted text in each row of purpose column 
    #namval is a list after including only first 2 rows of purpose column 
def splitted2():
    #a2 is the list of tokenised words of each row of purpose column
    a1=splitted1()[1]
    a2=[]
    for l in a1:
        b=[]
        for row in l:
            if re.search(r'\d+',row):
                row=row.strip('/').strip()
                b.append(row)
            if re.search(r'[a-zA-Z]+',row):
                for ch in ['-','(purposerevised)','(daterevised)','(subdivision)','(dateandpurposerevised)','rs.','rs','-from','to','from','re',' ','persha/','perunit/']:
                     if ch in row:
                        row=row.replace(ch,'').strip()
                b.append(row)
                
        a2.append(b)
    #namval1 is the list other than the things there in namval list
    namval1=[]
    for l in a1:
        b=[]
        cnt=0
        for row in l:
            if re.search(r'\d+',row):
                cnt+=1
                if cnt>2:
                    row=row.strip('/').strip()
                    b.append(row)
            if re.search(r'[a-zA-Z]+',row):
                for ch in ['-','(purposerevised)','(daterevised)','(subdivision)','(dateandpurposerevised)','rs.','rs','-from','to','from','re',' ','persha/','perunit/']:
                     if ch in row:
                        row=row.replace(ch,'').strip()
                cnt+=1
                if cnt>2:
                    b.append(row)
                
        namval1.append(b)
    namval2=[]
    for l in namval1:
        if len(l)==0:
            namval2.append(l)
            continue
        elif re.search(r'[^\d*\.?\d+]',l[-1]):
            l.pop(-1)
            namval2.append(l)
        else:
            namval2.append(l)
    return namval2,a2
    #namval2 is the list after removing unwanted text from namval1
    #n,n1 are the lists after removing the remaining unwanted text and to include only important things
def splitted3():
    n=[]
    n1=[]
    namval2=splitted2()[0]
    for l in namval2:
        if 'persha' in l:
            l.remove('persha')
        n.append(l)
    for l in n:
        l1=[]
        if len(l)==0:
            n1.append(l)
            continue
        for row in l:
            if re.search(r'[a-zA-Z]+',row):
                for ch in ['pershar','persha','pershand','persh','/','perunitforthefitquarteroffy','aand','and']:
                    if ch in row:
                        row=row.replace(ch,'').strip()
                l1.append(row)
            else:
                l1.append(row)
        n1.append(l1)
    n2=[]
    words=[]
    for l in n1:
        if len(l)==0:
            n2.append(l)
            continue
        else:
            for w in l:
                if re.search(r'[a-zA-Z]+',w):
                    break
                else:
                    l=l.remove(w)
                    if l is None:
                        l=[]
            n2.append(l)
    n2[-1]=[]
    #n2 is list after removing spaces,unwanted values
    return n2
def cap_red(capred):
    c=[]
    for cap in capred:
        if '[' in cap:
            cap=cap.replace('[','').replace(']','').replace('\'','').split(',')
            c.append(str(round(float(cap[0])/float(cap[1]),3)))
        else:
            c.append(cap)
    return c
def consolidate(capred):
    c1=[]
    for cap in capred:
        if '[' in cap:
            cap=cap.replace('[','').replace(']','').replace('\'','').split(',')
            c1.append(str(round(float(cap[2])/float(cap[3]),3)))
        else:
            c1.append(cap)
    return c1
def bonus_calc(bonus):
    bonus=[b.replace('\'','').replace('[','').replace(']','').replace(' ','') for b in bonus]
    bon=[]
    for b in bonus:
        if len(b)==0:
            bon.append('')
        else:
            x=b.split(',')
            bon.append(round(float((int(x[0])+int(x[1]))/int(x[1])),2)) 
    return(bon)
def split_calc(split1):
    split=[s.replace('\'','').replace('[','').replace(']','').replace(' ','') for s in split1]
    spl=[]
    for s in split:
        if len(s)==0:
            spl.append('')
        else:
            x=s.split(',')
            spl.append(str(round(float(int(x[1])/int(x[0])),3))) 
    return(spl)
def rights_calc(rights1):
    rights=[r.replace('\'','').replace('[','').replace(']','').replace(' ','').replace('\\','').replace('"','') for r in rights1]
    rits=[]
    for r in rights:
        if len(r)==0:
            rits.append('')
        else:
            if ':' in r:
                x=r.split(':')
            else:
                x=r.split(',')
            rits.append(str(round(float(int(x[0])/int(x[1])),3))) 
    return(rits)
def rightsshare_calc(rights1):
    rights=[r.replace('\'','').replace('[','').replace(']','').replace(' ','').replace('\\','').replace('"','') for r in rights1]
    rits=[]
    for r in rights:
        if len(r)==0:
            rits.append('')
        else:
            if ':' in r:
                x=r.split(':')
            else:
                x=r.split(',')
            rits.append(str(1+int(x[0])/int(x[1]))) 
    return(rits)
def return_of_capital(returnofcapital):
    split=[s.replace('\'','').replace('[','').replace(']','').replace(' ','') for s in returnofcapital]
    spl=[]
    for s in split:
        if len(s)==0:
            spl.append('')
        else:
            if ',' in s:
                x=s.split(',')
                spl.append(x[0])
            else:
                spl.append(s)
    return(spl)
def main():
    logger = create_logger()
    config = config_imports(logger)
    logger.info('Config == %s', config)
    namval=splitted1()[0]
    a2=splitted2()[1]
    n2=splitted3()
    interim1=[str(re.findall('\d*\.?\d+', str(l))) if l[0] in (['annualgeneralmeeting/interimdividend','inerimdividend','intdiv','intdividend','interimdiv','interimdividend','intermdividend','specialinterimdividend']) else '' for l in namval]
    interim2=[str(re.findall('\d*\.?\d+', str(l))) if (len(l)>=1 and l[0] in (['interimdividend'])) else '' for l in n2]
    split1=[str(re.findall('\d*\.?\d+', str(l))) if l[0] in (['facevaluesplit']) else '' for l in a2]
    split2=[str(re.findall('\d*\.?\d+', str(l))) if (len(l)>=1 and l[0] in (['facevaluesplit'])) else '' for l in n2]
    bonus=[str(re.findall('\d*\.?\d+', str(l))) if l[0] in (['bonus']) else '' for l in namval]
    finaldiv1=[str(re.findall('\d*\.?\d+', str(l))) if l[0] in (['annualgeneralmeeting/finaldividend', 'finaldividend']) else '' for l in namval]
    finaldiv2=[str(re.findall('\d*\.?\d+', str(l))) if (len(l)>=1 and l[0] in (['finaldividend'])) else '' for l in n2]
    spldiv1=[str(re.findall('\d*\.?\d+', str(l))) if l[0] in (['agm/spldiv', 'annualgeneralmeeting/specialdividend', 'specialdividend']) else '' for l in namval]
    spldiv2=[str(re.findall('\d*\.?\d+', str(l))) if (len(l)>=1 and l[0] in(['ndspecialdividend', 'specialdividend', 'splecialdividend'])) else '' for l in n2]
    fourthdist=[str(re.findall('\d*\.?\d+', str(l))) if l[0] in (['fourthdistribution', 'fourthdistributionintestpayment']) else '' for l in namval]
    div1=[str(re.findall('\d*\.?\d+', str(l))) if l[0] in (['annualgeneralmeeting/dividend', 'dividend']) else '' for l in namval]
    div2=[str(re.findall('\d*\.?\d+', str(l))) if (len(l)>=1 and l[0] in (['div', 'dividend'])) else '' for l in n2]
    rights1=[str(re.findall('\d*\d.?\d*', str(l))) if l[0] in (['rights', 'rights:']) else '' for l in namval]
    rights2=[str(l[1]) if (len(l)>=3 and l[0] in (['rights'])) else '' for l in n2]
    principle=[l[1] if (len(l)>=1 and l[0] in (['principle'])) else '' for l in n2]
    premium=[l[-1] if (len(l)>=1 and len(l)<3 and l[0] in (['@pmium', '@pmiumof'])) else l[-1] if (len(l)>3 and l[2] in (['@pmium', '@pmiumof'])) else '' for l in n2]
    returnofcapital=[str(re.findall('\d*\.?\d+', str(l))) if (len(l)>=1 and l[0] in (['turnofcapital'])) else '' for l in n2]
    firstdist=[str(re.findall('\d*\.?\d+', str(l))) if l[0] in (['fitdistributionintestpayment']) else '' for l in namval]
    capred=[str(re.findall('\d*\.?\d+', str(l))) if l[0] in (['capitalduction']) else '' for l in a2]
    capred1=cap_red(capred)
    consolidation=consolidate(capred)
    dist_int_pay=[str(re.findall('\d*\.?\d+', str(l))) if l[0] in (['distributionintest', 'distributionintestpayment']) else '' for l in namval]
    dist=[str(re.findall('\d*\.?\d+', str(l))) if l[0] in (['distribution']) else '' for l in namval]
    seconddist=[str(re.findall('\d*\.?\d+', str(l))) if l[0] in (['seconddistributionintestpayment']) else '' for l in namval]
    thirddist=[str(re.findall('\d*\.?\d+', str(l))) if l[0] in ('thirddistributionintestpayment') else '' for l in namval]
    df=splitted1()[2]
    df["Interim Div1"]=pd.DataFrame(interim1)
    df["Interim Div1"] = df["Interim Div1"].map(lambda x: re.sub(r'[^\d*\.?\d+]', '', x))
    df["Interim Div2"]=pd.DataFrame(interim2)
    df["Interim Div2"] = df["Interim Div2"].map(lambda x: re.sub(r'[^\d*\.?\d+]', '', x))
    df['Interim Div'] = df['Interim Div1'].str.cat(df['Interim Div2'], sep ="").replace('','1').astype(float)
    df["Face Split1"]=pd.DataFrame(split_calc(split1))
    df["Face Split2"]=pd.DataFrame(split_calc(split2))
    df['Face Split'] = df['Face Split1'].str.cat(df["Face Split2"], sep ="").replace('','1').astype(float)
    df["Bonus"]=pd.DataFrame(bonus_calc(bonus)).replace('','1').astype(float)
    df["Final Div1"]=pd.DataFrame(finaldiv1)
    df["Final Div1"] = df["Final Div1"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ')
    df["Final Div2"]=pd.DataFrame(finaldiv2)
    df["Final Div2"] = df["Final Div2"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ')
    df['Final Div'] = df['Final Div1'].str.cat(df['Final Div2'], sep ="").replace('','1').astype(float)
    df["Special Div1"]=pd.DataFrame(spldiv1)
    df["Special Div1"] = df["Special Div1"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ')
    df["Special Div2"]=pd.DataFrame(spldiv2)
    df["Special Div2"] = df["Special Div2"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ')
    df['Special Div'] = df['Special Div1'].str.cat(df['Special Div2'], sep ="").replace('','1').astype(float)
    df["Div1"]=pd.DataFrame(div1)
    df["Div1"] = df["Div1"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ')
    df["Div2"]=pd.DataFrame(div2)
    df["Div2"] = df["Div2"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ')
    df['Div'] = df['Div1'].str.cat(df['Div2'], sep ="").replace('','1').astype(float)
    df["Fourth Dist"]=pd.DataFrame(fourthdist)
    df["Fourth Dist"] = df["Fourth Dist"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ').replace('','1').astype(float)
    df["Rights1"]=pd.DataFrame(rights_calc(rights1))
    df["Rights2"]=pd.DataFrame(rights_calc(rights2))
    df['Rights'] = df['Rights1'].str.cat(df['Rights2'], sep ="").replace('','1').astype(float)
    df["Rightscalc1"]=pd.DataFrame(rightsshare_calc(rights1))
    df["Rightscalc2"]=pd.DataFrame(rightsshare_calc(rights2))
    df['Rightscalc'] = df['Rightscalc1'].str.cat(df['Rightscalc2'], sep ="").replace('','1').astype(float)
    df["First Dist"]=pd.DataFrame(firstdist)
    df["First Dist"] = df["First Dist"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ').replace('','1').astype(float)
    df["Capital Reduction"]=pd.DataFrame(capred1).replace('','1').astype(float)
    df["Consolidation"]=pd.DataFrame(consolidation).replace('','1').astype(float)
    df["Dist Interest Payment"]=pd.DataFrame(dist_int_pay)
    df["Dist Interest Payment"] = df["Dist Interest Payment"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ').replace('','1').astype(float)
    df["Distribution"]=pd.DataFrame(dist)
    df["Distribution"] = df["Distribution"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ').replace('','1').astype(float)
    df["Second Dist"]=pd.DataFrame(seconddist)
    df["Second Dist"] = df["Second Dist"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ').replace('','1').astype(float)
    df["Third Dist"]=pd.DataFrame(thirddist)
    df["Third Dist"] = df["Third Dist"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ').replace('','1').astype(float)
    df["Premium"]=pd.DataFrame(premium)
    df["Premium"] = df["Premium"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ').replace('','1').astype(float)
    df['Rights']=(df['Rights']*df['Premium'])
    df["Principle"]=pd.DataFrame(principle)
    df["Principle"] = df["Principle"].map(lambda x: re.sub(r'[^\d*\.?\d+,]', '', x)).str.replace(',',' ').replace('','1').astype(float)
    df["Return of Capital"]=pd.DataFrame(return_of_capital(returnofcapital)).replace('','1').astype(float)
    df=df.drop(["Interim Div1","Interim Div2",'Special Div1',"Special Div2","Final Div1","Final Div2","Rights1","Rights2","Div1","Div2","Face Split1","Face Split2","Rightscalc1","Rightscalc2","Premium"],axis=1)
    df.to_csv('../outputs/cor_act_with_fac.csv')
    print("Sucessfully created csv after data cleaning")
if __name__ == '__main__':
    main()




































