# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 12:56:37 2023

@author: axel4
"""

import datetime
import time
import requests
import json
import re
import numpy as np

import pandas as pd
from bs4 import BeautifulSoup as bs
import selenium

import datetime
import time
import requests
import json
import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium import webdriver
#import webbrowser
import math 
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
from selenium.webdriver.support.relative_locator import locate_with

import datetime
#Import NBA games boxscores

import pickle 
a_file_o = open("data_winwindraw.pkl", "rb")
dico = pickle.load(a_file_o)
a_file_o.close()


#Import historical data
#import pickle 
#a_file_nhl = open("data_windrawwin.pkl", "rb")
#dico = pickle.load(a_file_nhl)
#a_file_nhl.close()

#dico=dict()

a = pd.date_range(list(dico.keys())[-1], datetime.date.today()-datetime.timedelta(days=1))
#dates des matchs
col_data=['League','Result', 'Stake', 'Prediction type','Prediction score', 'Success']
for date in a:
    if len(str(date.month))==1:
        mth='0'+str(date.month)
    else:
        mth=str(date.month)
    
    if len(str(date.day))==1:
        dy='0'+str(date.day)
    else:
        dy=str(date.day)
    url="https://www.windrawwin.com/predictions/history/"+str(date.year)+mth+dy
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"})
    html = response.text
    soup = bs(html, "lxml", from_encoding="utf-8")
    matches=soup.findAll("div", {"class":"prfl w100p darkrow ptcont mt20"})
    tables=soup.findAll("div", {"class":"widetable"})
    time.sleep(0.5)

    datatables=[]

    for matche,table in zip(matches,tables):
        league=matche.find("div",{"class":"ptleag"}).text
        tab6col = table.findAll('table')[0]
        datatable=[]
        for record in tab6col.find_all('tr'):
            temp_data = []
            for data in record.find_all('td'):
                if data.find("img") is not None:
                    temp_data.append(data.find("img").attrs["alt"])
                    break
                else:
                     temp_data.append(str(re.sub("[A-Z]\.(.*?)$|","",data.text)))
            for data in record.find_all('th'):
                temp_data.append(str(data.text))
            datatable.append(temp_data)
        
        for i in range(1,len(datatable)-1):
            datatable[i]=[league]+datatable[i]
    
            datatables.append(datatable[i])
    
    df = pd.DataFrame(datatables,columns=col_data)
    df.Success=df.Success.apply(lambda x:x.replace(" Prediction",""))

    dico[date]=df
    
    
a_file = open("data_winwindraw.pkl", "wb")
pickle.dump(dico, a_file)
a_file.close()


fff=pd.concat(dico.values(),axis=0)
fff["Target"]=fff.Success.apply(lambda x :  0 if re.match("Incorrect Match",x) is not None else 2 if  re.match("Correct Score",x)else 1 )
fff["Target_Match"]=fff.Success.apply(lambda x :  0 if re.match("Incorrect Match",x) is not None else 1 )
fff["Target_Score"]=fff.Success.apply(lambda x :  1 if re.match("Correct Score",x) is not None else 0 )

fff_ML0=fff.groupby(["League"]).agg(
    {
        'Target_Match': ["sum", "count","mean"],
        'Target_Score': ["sum", "count","mean"]
    }
)

fff_ML=fff.groupby(["League","Stake"]).agg(
    {
        'Target_Match': ["sum", "count","mean"],
        'Target_Score': ["sum", "count","mean"]
    }
)




    



