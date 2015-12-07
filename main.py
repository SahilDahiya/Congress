from urllib.request import urlopen
import pandas as pd
import json
from bs4 import BeautifulSoup
import re
import time
from os import walk





def congress_member(chamber,congress_no):
    url='http://api.nytimes.com/svc/politics/v3/us/legislative/congress/'+congress_no+'/'+chamber+'/members.json?api-key=6b71fe6473edf106024f422ae35260d5%3A14%3A70897826'
    response = urlopen(url).read().decode('utf8')
    js=json.loads(response)
    result=js['results'][0]
    member=result['members']
#Converting json into Panda DataFrame    
    for x in range(0,len(member)):
        data=pd.DataFrame.from_dict(member[x],orient='index')
        if x==0:
            df=data.transpose()
        else:
            data_trans=data.transpose()
            df=df.append(data_trans)
    return df
    
    
#senate113=congress_member(chamber='senate',congress_no='113')
#House99=congress_member(chamber='house',congress_no='99')


#function  for extracting the bill no.
def getBill(bill_html):
    bill_raw=bill_html.find_all('span',attrs={'class':'a'})
    bill_list=[]
    for b in bill_raw:
        m = re.search('>(.+?)(-|<)',str(b))
        if m:
            bill_list.append(m.group(1))
    return bill_list

#function  for extracting the congress no.    
def getCongress(bill_html):
    congress_raw=bill_html.find_all('span',attrs={'class':''})
    congress_list=[]
    for c in congress_raw:
        m = re.search('>(.+?)th congress',str(c))
        if m:
            congress_list.append(m.group(1)[1:])
    return congress_list

#function for extracting bill and congress no. from particular page    
def billByIssueByPage(issue,page):
    url='https://www.opencongress.org/issues/defunct/'+issue+'?page='+str(page)
    response = urlopen(url).read().decode('utf8')
    soup = BeautifulSoup(response, 'html.parser')
    bill_html=soup.body.find('ul',attrs={'class':'bills_list'})
    bill=getBill(bill_html)
    congress=getCongress(bill_html)
    error=[]
    dict={}
    if len(bill)!=len(congress):
        error.append('error on page '+str(page))
    else:
        for x in range(len(bill)):
            dict[bill[x]]=congress[x]
    return dict,error
        
        
#page2Health,error=billByIssueByPage(issue='8442_health',page=2)  
#page13Consumer_credit,error=billByIssueByPage(issue='4168_consumer_credit',page=13)

#==============================================================================
# Remember to add few more bills from first page
#==============================================================================
        
def billsByIssue(cause):
    firstpage='https://www.opencongress.org/issues/defunct/'+str(cause)
    response_fp = urlopen(firstpage).read().decode('utf8')
    soup_fp = BeautifulSoup(response_fp, 'html.parser')        
    total_bill_page=soup_fp.body.find('div',attrs={'class':'pagination'}).text
    max_no=max([int(s) for s in total_bill_page.split() if s.isdigit()])
    total_bill={}
    error=[]
    for i in range(1,max_no+1):
        dict,errorByPage=billByIssueByPage(issue=cause,page=i)        
        total_bill.update(dict)
        if len(errorByPage)!=0:
            error.append(error[0])
    return {cause:total_bill},error
    
#consumer_credit_bill,error=billsByIssue(cause='4168_consumer_credit')
#seaFood,error_seaFood=billsByIssue(cause='7113_seafood')

    
#getting the years from govtrack.us
def getYearsOrVoteId(url):
    response = urlopen(url).read().decode('utf8')
    soup= BeautifulSoup(response, 'html.parser')
    text_html=soup.find_all('a')
    text=[]
    for x in range(1,len(text_html)):
        m = re.search('<a href="(.+?)/"',str(text_html[x]))
        if m:
            text.append(m.group(1))
    return text
    
def VoteNumberByYear(congress):
    url='https://www.govtrack.us/data/congress/'+str(congress)+'/votes/'
    years=getYearsOrVoteId(url)
    for y in years:
        url1=url+y+'/'
        VoteId=getYearsOrVoteId(url1)
        for v in VoteId:
            url2=url1+str(v)+'/data.json'
            st=y+v
            print(st)
            response = urlopen(url2).read().decode('utf8')
            js=json.loads(response)
            file='E:\Congress\\'+str(congress)+'\_'+y+'_'+v+'.csv'
            with open(file, 'w') as outfile:
                json.dump(js, outfile,ensure_ascii=False)            
            time.sleep(1)
    
    
#VoteNumberByYear(113)
#VoteNumberByYear(112)
#VoteNumberByYear(111)
#VoteNumberByYear(110)
 

def CombineVotes(congress):
    f = []
    for (dirpath, dirnames, filenames) in walk('E:\Congress\\'+str(congress)):
        f.extend(filenames)
        break
        # Reading data back
    t4=pd.DataFrame()
    for d in f:
        file="E:\Congress\\"+str(congress)+"\\"+d
        with open(file, 'r') as f:
             data = json.load(f)             
        t3=pd.DataFrame()
        for k in list(data['votes'].keys()):
            t2=pd.DataFrame()
            for x in range(len(data['votes'][k])):
                t=data['votes'][k][x]
                t1=pd.DataFrame.from_dict(t,orient='index')
                if x==0:
                    t2=t1.transpose()
                    t2['Vote']=k
                else:
                    t2=t2.append(t1.transpose(),ignore_index=True)
                    t2['Vote']=k
            t3=t3.append(t2,ignore_index=True)
            t3['Vote_Id']=data['vote_id']
        t4=t4.append(t3,ignore_index=True)
    print(str(congress)+" is done")
    return t4
    
#Roll_113=CombineVotes(113)
#Roll_113.to_csv('E:\Congress\Combined\RollCall_113.csv') 

#Roll_112=CombineVotes(112)
#Roll_112.to_csv('E:\Congress\Combined\RollCall_112.csv')
#
#Roll_111=CombineVotes(111)
#Roll_111.to_csv('E:\Congress\Combined\RollCall_111.csv')
#
#Roll_110=CombineVotes(110)
#Roll_110.to_csv('E:\Congress\Combined\RollCall_110.csv')
