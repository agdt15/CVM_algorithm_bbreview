# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 13:10:39 2023

@author: axel4
"""
import selenium

#import webbrowser
import math 
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import pickle
import copy


options = Options()
options.add_argument('--headless')
options.add_experimental_option("w3c", True)


#SELENIUM SCRAPPING
driver = webdriver.Chrome(options=options)
url_base="https://www.euroclubindex.com/match-odds/"
driver.get(url_base)
time.sleep(10)
#On utilise Select car on doit refresh la page via la selection dans le menu select 
from selenium.webdriver.support.ui import Select
l = Select(driver.find_element(By.CSS_SELECTOR,'select'))
## click button
#On peut enumerer le nombre d'options qu'il y a dans le menu donc on itere pour recupérer toutes les pages  
soups2=[]
for j in range(len(l.options)-1):
    l.select_by_index(j)
    time.sleep(10)
    soups2.append(bs(driver.page_source, 'lxml'))


driver.close() 
#FIN SCRAPPING



#RECUPERATION DES TABLEAUW DE MATCHS 
k=[]
for soup in soups2:
    games=[]
    for row in soup.findAll("div",{"class":"module-match-odds__item d-block"}):
        games.append(row)
    league=soup.find("div",{"class":"col-lg-5 mb-3 mb-lg-0"}).text
    k.append([row.find('div', class_='module-match-odds__item-date').text.strip(),row.find('div', class_='module-match-odds__item-hometeam-info').text.strip()
    ,row.find('div', class_='module-match-odds__item-awayteam-info').text.strip()
    ,row.find('div', class_='module-match-odds__item-score').text.strip()
    ,row.find('div', class_='module-match-odds__item-cup-home').text.strip()+"-"+row.find('div', class_='module-match-odds__item-draw').text.strip()
    +"-"+row.find('div', class_='module-match-odds__item-cup-away').text.strip()]+[league])
        


dfs=pd.DataFrame(k)
dfs.columns=["Date","Home","Away","Results","Probs","League"]


#On recupère le score si match terminé (refresh peut attendre une journée sur le site)

dfs.Results = dfs.Results.apply(lambda x: re.search(r"[0-9]{1,2} \- [0-9]{1,2}", x)[0] if re.search(r"[0-9]{1,2} \- [0-9]{1,2}", x) is not None else "")


# ...

#dfs.Results=dfs.Results.apply(lambda x: re.search("[0-9]{1,2} \- [0-9]{1,2}",x)[0] if re.search("[0-9]{1,2} \- [0-9]{1,2}",x) is not None else "" )
#On recupère les probas 
dfs.Probs=dfs.Probs.apply(lambda x:x.replace("-",""))
dfs.Probs=dfs.Probs.apply(lambda x: [float(list(map(str.strip,x.split("%")))[i])/100 for i in [0,1,2]])
#On transforme les probas en cotes
dfs["H_odd"]=dfs.Probs.apply(lambda x: 1/x[0])
dfs["D_odd"]=dfs.Probs.apply(lambda x: 1/x[1])
dfs["A_odd"]=dfs.Probs.apply(lambda x: 1/x[2])

#Traitement pour clean les noms d'equipe
#dfs.Home=dfs.Home.apply(lambda x:re.sub("\([0-9]+\)","",x))
#dfs.Away=dfs.Away.apply(lambda x:re.sub("\([0-9]+\)","",x))
dfs.Home = dfs.Home.apply(lambda x: re.sub(r"\([0-9]+\)", "", x))
dfs.Away = dfs.Away.apply(lambda x: re.sub(r"\([0-9]+\)", "", x))
dfs["Match"]=dfs["Home"]+" - "+dfs["Away"]

#RECUPERATION DES SCORES SI EXISTE
dfs["Score_1"]=dfs.Results.apply(lambda x: int(x.split("-")[0]) if len(x)>0 else np.nan)
dfs["Score_2"]=dfs.Results.apply(lambda x: int(x.split("-")[1]) if len(x)>0 else np.nan)

#RESULTAT et cote du vainqueur DU MATCH SI EXISTE 
wins=[]
wins_odd=[]
for home,away,h,d,a in zip(dfs.Score_1,dfs.Score_2,dfs.H_odd,dfs.D_odd,dfs.A_odd):
    if home>away and home>=0:
        wins.append("Home")
        wins_odd.append(h)
    elif away>home and home>=0:
        wins.append("Away")
        wins_odd.append(a)
    elif away==home and home>=0:
        wins.append("Draw")
        wins_odd.append(d)
    else:
        wins.append("Not_yet")
        wins_odd.append(np.nan)
        
dfs["Winner"]=wins
dfs["Winning_odd"]=wins_odd


#Traitement de la date
import datetime
year_now=2023
dfs["Date"]=dfs.Date.apply(lambda x:datetime.datetime.strptime(x+" 2023",'%d %b %Y').date())

#FIN DU TRAITEMENT






#LOAD DICO GAMES
a_file_pre = open("euro_index2.pkl", "rb")
dico_games=pickle.load(a_file_pre)
a_file_pre.close()
print("\n")
print("Load "+" Euro Index "+ "file")  

for day in set(dfs.Date):
    if day in dico_games.keys():
        print(day)
        # Check if the DataFrame already exists in the dictionary
        existing_df = dico_games[day]
        existing_df["Match"]= existing_df["Home"]+" - "+ existing_df["Away"]
        new_data = dfs[dfs.Date == day]
        # Filter rows in `dfs` for the current day
        

        if not existing_df.empty:
            # If the DataFrame in the dictionary is not empty, update it
            existing_df=existing_df.drop_duplicates(subset="Match").set_index("Match")
            new_data=new_data.drop_duplicates(subset="Match").reset_index(drop=True).set_index("Match")
            
            existing_df["Match"]= existing_df["Home"]+" - "+ existing_df["Away"]
            new_data["Match"]= new_data["Home"]+" - "+ new_data["Away"]
            
            combined_df = pd.concat([existing_df, new_data[~new_data.index.isin(existing_df.index)]], ignore_index=True)
            # Update the existing DataFrame with new values, if available
            
            combined_df.Results.update(new_data.Results)
            combined_df.Score_1.update(new_data.Score_1)
            combined_df.Score_2.update(new_data.Score_2)
            combined_df.Winner.update(new_data.Winner)
            
            wins = np.select(
            [combined_df.Score_1 > combined_df.Score_2, combined_df.Score_1 < combined_df.Score_2,
             combined_df.Score_1 == combined_df.Score_2],
            ["Home", "Away", "Draw"],
            default="Not_yet"
            )
            
            wins_odd = np.select(
            [combined_df.Score_1 > combined_df.Score_2, combined_df.Score_1 < combined_df.Score_2,
             combined_df.Score_1 == combined_df.Score_2],
            [combined_df.H_odd, combined_df.A_odd, combined_df.D_odd],
            default=np.nan
        )

            combined_df["Winner"] = wins
            combined_df["Winning_odd"] = wins_odd
            
            #combined_df.Winning_odd.update(new_data.Winning_odd)

            # Reset the index back to its original state
            combined_df.reset_index(inplace=True,drop=True)
            dico_games[day] = combined_df
        else:
            # If the DataFrame in the dictionary is empty, assign the new data
            print("T CHelOU")
            dico_games[day] = new_data
    else:
        # If the date does not exist in the dictionary, add it with the new data7
        print("new day data")
        print(day)
        dico_games[day] = dfs[dfs.Date == day]
  
for keys in dico_games.keys():
    dico_games[keys]=dico_games[keys][['Date', 'Home', 'Away', 'Results', 'Probs', 'League', 'H_odd', 'D_odd',
       'A_odd', 'Score_1', 'Score_2', 'Winner', 'Winning_odd','Match']]


d_keys,d_values=copy.deepcopy(list(dico_games.keys())),copy.deepcopy(list(dico_games.values()))
for d, v in zip(d_keys,d_values):
    if d<datetime.date(2023,6,1):
        print("OK")
        del dico_games[d]
        print("del")
        d=datetime.date(2024,d.month,d.day)
        print(d)
        dico_games[d]=v
       
#SAVE AND UPDATE DICO GAMES
a_file_pre = open("euro_index.pkl", "wb")
pickle.dump(dico_games,a_file_pre)
a_file_pre.close()
print("\n")
print("Save "+"Euro Index" +" file")  





    

