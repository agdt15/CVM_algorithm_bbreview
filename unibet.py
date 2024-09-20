# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 19:23:32 2023

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
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from odds_scrapper4 import * 


def calcul_surebet(cote_a,cote_b):
    return 1/(1/cote_a+1/cote_b)

data = [['Alejandro Tabilo ', '7 ', '3 ', '2 ', '0 '],
        ['Alejandro Davidovich Fokina ', '6 ', '6 ', '0 ', '0 ']]

def convertir_score_tennis(data):
  """
  Converti une liste de listes représentant les scores d'un match de tennis au format "7-6 3-6 2-0 : 0:0".

  Args:
    data: Une liste de listes contenant les scores des sets.

  Returns:
    La chaîne formatée représentant le score du match.
  """

  score_match = ""
  scores_jeux = [str(score1).strip()+"-"+str(score2).strip() for score1,score2 in zip(data[0][1:-1],data[1][1:-1])]
  score_set = " ".join(scores_jeux)
  point_set = f"{str(data[0][-1]).strip()}-{str(data[1][-1]).strip()}"

  score_match += ": 0:0"
  return score_set, point_set

score_final = convertir_score_tennis(data)
print(score_final)  # Sortie: 7-6 3-6 2-0 : 0:0



def scroll_to_endpage(driver):
    #On doit scroller jusqu'a la fin de la page pour charger toutes les données
    #ce script permet de faire un scroll vers la fin de page (infini si besoin, utilisable pour insta ou linkedin)
    SCROLL_PAUSE_TIME = 0.5
    
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
    
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_match_data(match_element):
  """
  This function extracts match data from the provided element,
  handling cases where trend elements might be missing and avoiding zip errors.

  Args:
      match_element (BeautifulSoup element): The BeautifulSoup element containing the match data.

  Returns:
      dict: A dictionary with player names as keys and their odds and progress data as values.
          If a trend element is not found, the "pct" value will be None.
  """
  match_data = {}
  labels = match_element.find_all("div", class_="oddbox-label")
  values = match_element.find_all("div", class_="oddbox-value")
  trends = match_element.find_all("div", class_="oddbox-trend")
  competition = match_element.find("span").text

  # Ensure all lists have the same length (considering empty lists)
  num_players = max(len(labels), len(values), len(trends))

  for i in range(num_players):
    player_name = labels[i].find("span").text  # Extract player name
    odds = values[i].find("span").text  # Extract odds value

    # Check if trend element exists for this player
    trend_element = None if i >= len(trends) else trends[i]
    pct = None  # Initialize pct as None (default for missing trend)

    if trend_element:
      pct = float(trend_element.em.get("style").replace("width: ", "").replace(";", "").replace("%", ""))  # Get progress bar style

    # Create dictionary entry for the player
    match_data[player_name] = {"odds": odds, "percentDistribution": pct}
  match_data["Competition"] = competition

  return match_data

class Unibet(OddsScraper):
    def __init__(self,sport,type_scrap,mise_base,date,delta=0,verbose=False,headless=True):
        self.sport=sport
        self.date=date
        self.bookmaker="unibet"
        self.type_scrap=type_scrap
        self.sport_url = "https://www.unibet.fr/sport/"+str(dico_sports[sport]["sport_id"]["Unibet"])
        self.pause=dico_sports[sport]["pause"]
        self.data="./Data/"+self.sport+"/data_"+self.sport.lower()+"_"+self.type_scrap+"_"+self.bookmaker+"_"+str(self.date+datetime.timedelta(hours=+delta)).replace("-","")+".pkl"
        self.data2="./Data/"+self.sport+"/data_"+self.sport.lower()+"_"+self.type_scrap+"_"+self.bookmaker+"_"+str(self.date+datetime.timedelta(hours=+24+delta)).replace("-","")+".pkl"
        
        #self.headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        self.headers=generate_random_headers()
        self.mise_base=mise_base
        self.verbose=verbose
        self.headless=headless
        
    def scrape_live(self,surbet=False):
        #LOAD PRE LIVE ODDS
        a_file_pre = open("./Data/"+self.sport+"/data_"+self.sport.lower()+"_pre_"+self.bookmaker+"_"+str(datetime.date.today()).replace("-","")+".pkl", "rb")
        print("load data_"+self.sport.lower()+"_pre_"+self.bookmaker+"_"+str(datetime.date.today()).replace("-","")+".pkl")
        self.dico_pre=pickle.load(a_file_pre)
        a_file_pre.close()
        
        if len(self.dico_pre)>0:
           self.dico_pre=self.dico_pre[list(self.dico_pre.keys())[-1]]
                
        #LAUNCH UNIBET SESSION
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        
        driver = webdriver.Chrome(options=chrome_options)
        #driver = webdriver.Chrome()
        #driver.get("https://www.unibet.fr/sport/tennis")
        driver.get(self.sport_url)
        
        #click cookies first connection
        try:
             WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.Xpath,'//*[@id="onetrust-close-btn-container"]/button'))).click()
        except:
            pass
        
        #SCROLL
        #scroll_to_endpage(driver=driver)
        

        time.sleep(5)
        # TOOGLE MORE LIVE EVENTS
        # LOOKING FOR CLICK BUTTON 
        try:
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="view__event"]/div/div/div/div/span'))).click()
        except:
            pass
        
        soup2=bs(driver.page_source, 'lxml')
        self.soup=soup2
        #get matches
        self.list_match_lives=soup2.find("div",{"class":"liveEventsWrapper"}).findAll("section",{"id":"cps-eventcard-live"})
        
        
        self.track_record={}
        ##### A DECKARER 
        
        c = 0
        while len(self.list_match_lives) > 0:
            c+=1
            print(c)
            
            if c % 10 == 0 :
                print("save data")
                self.save_data()
            
            # TOOGLE MORE LIVE EVENTS
            # LOOKING FOR CLICK BUTTON 
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="view__event"]/div/div/div/div/span'))).click()
            except:
                pass
            
            time_stamp=datetime.datetime.today().time()
            soup2=bs(driver.page_source, 'lxml')
            self.list_match_lives=soup2.find("div",{"class":"liveEventsWrapper"}).findAll("section",{"id":"cps-eventcard-live"}) 
            
            
            for live_match in self.list_match_lives:
                try:
                    home_team=live_match.find("span",{"class":"home"}).text.strip()
                    away_team=live_match.find("span",{"class":"away"}).text.strip()
                except AttributeError:
                    home_team=live_match.findAll("span",{"class":""})[0].text.strip()
                    away_team=live_match.findAll("span",{"class":""})[2].text.strip()
                match_name=" - ".join([home_team,away_team])
                competition=live_match.find("p").text
                
                try:
                    scores=live_match.find("span",{"class":"score"}).text
                except:
                    tab6col=live_match.find('table',{"class":"inplay-table-board-table"})
                    datatable=[]
                    for record in tab6col.find_all('tr'):
                        temp_data = []
                        for data in record.find_all(['td', 'th']):
                            if data.name == 'td': 
                                temp_data.append(str(re.sub("[A-Z]\.(.*?)$|","",data.text)))
                            elif data.name == 'th':
                                temp_data.append(str(data.text))
                        datatable.append(temp_data)
                        scores=convertir_score_tennis(temp_data)
                        
                list_match=[]
                for j in live_match.findAll("div",{"class":"oddbox-content"}):
                    list_match.append([i.text for i in j.findAll("span")])
                    
                dico_match_live={"Vainqueur" : dict(list_match), "Competition" : competition, "Score" : scores}
                
                
                #MISE A JOUR DU DICO
                if match_name in self.dico.keys():
                    self.dico[match_name].update({str(time_stamp.hour)+"h"+str(time_stamp.minute)+"."+str(time_stamp.second) : dico_match_live})
                else :
                    self.dico[match_name]={str(time_stamp.hour)+"h"+str(time_stamp.minute)+"."+str(time_stamp.second) : dico_match_live }
                    
                    
                 #### ALERTE FIN DE MATCH 
                 
                 
                #EVALUATION DES COTES
                if surbet:
                    try :
                        dico_pre=self.dico_pre[match_name]
                        type_bets=self.dico[match_name]
                        
                        if match_name not in self.track_record.keys():
                            self.track_record[match_name]={"surebet":99}
        
                        j1,j2=match_name.split(" - ")
                        if float(dico_pre["Vainqueur"][j1])>float(dico_pre["Vainqueur"][j2]):
                            a=float(dico_pre["Vainqueur"][j1])
                            surebet=round(calcul_surebet(a,float(type_bets["Vainqueur"][j2])),2)
                            mise=round(self.mise_base*a/float(type_bets["Vainqueur"][j2]),2)
                            if surebet<1:
                                pass
                            else :
                                if self.track_record[match_name]["surebet"]==surebet:
                                    pass
                                else:
                                    send_telegram_alert("{} at {} \n Surebet = {} \n Mise ={}".format(j2,float(type_bets["Vainqueur"][j2]),surebet,mise),self.sport)
                            self.track_record.update({match_name:{"surebet":surebet}})  
                        else :
                            a=float(dico_pre["Vainqueur"][j2])
                            surebet=round(calcul_surebet(a,float(type_bets["Vainqueur"][j1])),2)
                            mise=round(self.mise_base*a/float(type_bets["Vainqueur"][j1]),2)
                            if surebet<1.05 and surebet>0.92:
                                pass
                            else :
                                 if self.track_record[match_name]["surebet"]==surebet:
                                    pass
                                 else:
                                     send_telegram_alert("{} at {} \n Surebet = {} \n Mise ={}".format(j1,float(type_bets["Vainqueur"][j1]),surebet,mise),self.sport)
                            
                            self.track_record.update({match_name:{"surebet":surebet}})
                    except KeyError:
                        pass
            
            time.sleep(random.randint(self.pause,self.pause+5))
        
        driver.close()
            
            
            
            
    def get_prematch(self):
        self.dico={}
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(self.sport_url)
        time.sleep(10)
        
        #SCROLLING INFINI
        ###############################################################################
        scroll_to_endpage(driver=driver)
        ###############################################################################

        soup3=bs(driver.page_source, 'lxml')
    
        # Select the main events container
        events_container = soup3.select_one("#cps-eventsdays-list")

        if events_container:  # Check if the container exists
            # Process individual matches
            for match_element in events_container.find_all("section", class_="eventcard--toplight"):
                # Extract match data
                match_data = extract_match_data(match_element)
                match_name=" - ".join([play for play in list(match_data.keys()) if play!="Competition" and play!="Match nul"])
                if len(match_data) == 0:
                    print("pas de data : on passe")
                    continue

                # Process and print matchata
                print("-" * 50)  # Optional separator for clarity
                print("Match Data:")
                for key, value in match_data.items():
                    print(f"- {key}: {value}")

                # Extract and print date from parent element
                date_element = match_element.parent.parent.select_one("div.eventsday_header.app23__text-bold-xl").text
                if date_element:
                    print(f"\nDate: {date_element}")
                competition = match_data['Competition']
                del match_data['Competition']
                
                self.dico[match_name]={"Vainqueur": match_data, "Date": date_element, "Competition": competition}
                
                
            dico_dates={}
            for match_name, match_data in self.dico.items():
                print(match_name)
                print(match_data)
                
                # Extraire la date du dictionnaire match_data
                date_element = dateparser.parse(match_data["Date"]).date()
              
                # Créer un dictionnaire pour stocker les matchs par date (si ce n'est pas déjà fait)
                if date_element not in dico_dates:
                  dico_dates[date_element] = {}
              
                # Ajouter le match actuel au dictionnaire pour la date correspondante
                dico_dates[date_element][match_name] = match_data
            self.dico_dates=dico_dates
            self.dates=list(dico_dates.keys())
        else :
            self.dates=[]

                        
        driver.close()
    
    def scrap_live_forced(self):
                try:
                    self.scrape_live()
                except IndexError:
                    randomtime = random.randint(5,10)
                    print('ERROR - Retrying again website {} retrying in {} secs'.format(self.sport_url, randomtime))
                    self.save_data()
                    time.sleep(randomtime)
                    self.scrape_live()
                except ConnectionError as e:
                    print("Connection error:", e)
                    randomtime = random.randint(1,5)
                    print('ERROR - Retrying again website {}, retrying in {} secs'.format(self.sport_url, randomtime))
                    self.save_data()
                    time.sleep(randomtime)
                    self.scrape_live()
                except requests.exceptions.Timeout as e:
                    print("Timeout error:", e)
                    pass
                except requests.exceptions.RequestException as e:
                    print("Error:", e)
                    pass     
                finally:
                    pass
                
    def scrape(self):
        if self.type_scrap=="live":
            self.scrap_live_forced()
                
        elif self.type_scrap=="pre":
            self.get_prematch()
            
            

    