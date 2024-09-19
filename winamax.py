# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 16:35:14 2023

@author: axel4
"""
import datetime
import time
import requests
import json
import random
import pickle

import random
import string
from requests import Session
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from odds_scrapper4 import * 

class Winamax(OddsScraper):
    def __init__(self,sport,type_scrap,mise_base,delta=0,verbose=True,headless=True):
        self.sport=sport
        self.bookmaker="winamax"
        self.type_scrap=type_scrap
        self.sport_url = "https://www.winamax.fr/paris-sportifs/sports/"+str(dico_sports[sport]["sport_id"]["Winamax"])
        self.pause=dico_sports[sport]["pause"]
        self.data="data_"+self.sport.lower()+"_"+self.type_scrap+"_"+self.bookmaker+"_"+str(datetime.date.today()+datetime.timedelta(hours=+delta)).replace("-","")+".pkl"
        self.data2="data_"+self.sport.lower()+"_"+self.type_scrap+"_"+self.bookmaker+"_"+str(datetime.date.today()+datetime.timedelta(hours=+24+delta)).replace("-","")+".pkl"
        #self.headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        self.headers=generate_random_headers()
        self.mise_base=mise_base
        self.verbose=verbose
        self.headless=headless
        self.c=0
        
    def scrape_live(self):
        #load pre live 
        a_file_pre = open("data_"+self.sport.lower()+"_pre"+"_"+self.bookmaker+"_"+str(datetime.date.today()).replace("-","")+".pkl", "rb")
        self.dico_pre=pickle.load(a_file_pre)
        a_file_pre.close()
        
        chrome_options = Options()
        if self.headless:    
            chrome_options.add_argument('--headless')
            
        driver = webdriver.Chrome(options=chrome_options)
        #driver = webdriver.Chrome()
        driver.get(self.sport_url)
        #driver.get("https://www.winamax.fr/paris-sportifs/sports/5")
        time.sleep(1)
        try:
             l2 = driver.find_element(By.ID,'tarteaucitronAllDenied2')
             ## click button
             driver.execute_script("arguments[0].click();", l2);
        except:
            pass
        finally:
            time.sleep(1)
            l2 = driver.find_element(By.CSS_SELECTOR,'button')
            ## click button
            driver.execute_script("arguments[0].click();", l2);
        
        s = Session()
        # Reddit will think we are a bot if we have the wrong user agent
        selenium_user_agent = driver.execute_script("return navigator.userAgent;")
        s.headers.update({"user-agent": selenium_user_agent})
        for cookie in driver.get_cookies():
            s.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
        
        #response = requests.get(self.sport_url, headers=self.headers)
        response = s.get(self.sport_url)
        html = response.text
        split1 = html.split("var PRELOADED_STATE = ")[1]
        split2 = split1.split(";</script>")[0]
        
        
        
        
        json2 = json.loads(split2)
        today = datetime.datetime.today() + datetime.timedelta(hours=+12)
        # recuperation des ids des matchs de la soirée uniquement (les matches qui sont dans maximum 12h (ligne precedente))
        self.id_list = {key:val for key, val in json2["matches"].items() if val["sportId"] == int(dico_sports[self.sport]["sport_id"]["Winamax"]) and val["matchStart"] <= today.timestamp()}
        self.track_record={}
        c = 2
        
        while len([self.id_list[key]["matchStart"] for key in list(self.id_list) if self.id_list[key]["status"] == "LIVE"]) > 0 and c<500:
            a, b = 1, 1
            c += 1
            self.c=c
            if c % 3 == 0:
                #response = requests.get(self.sport_url, headers=self.headers)
                response = s.get(self.sport_url)
                html = response.text
                split1 = html.split("var PRELOADED_STATE = ")[1]
                split2 = split1.split(";</script>")[0]
                json2 = json.loads(split2)
                today = datetime.datetime.today() + datetime.timedelta(hours=+12)
                # recuperation des ids des matchs de la soirée uniquement (les matches qui sont dans maximum 12h (ligne precedente))
                self.id_list = {key:val for key, val in json2["matches"].items() if val["sportId"] == int(dico_sports[self.sport]["sport_id"]["Winamax"]) and val["matchStart"] <= today.timestamp() and val["status"] == "LIVE" }
            
            elif c % 10 ==0 :
                print("save data ??")
                self.save_data()
                self.commit_data()
            
            for match_name in self.id_list.keys():
                type_bets = {}
                url = "https://www.winamax.fr/paris-sportifs/match/" + str(match_name)
                #response = requests.get(url, headers=self.headers)
                response = s.get(url, headers=self.headers)
                html = response.text
                split11 = html.split("var PRELOADED_STATE = ")[1]
                split22 = split11.split(";</script>")[0]
                json3 = json.loads(split22)
                
                try :
                    bet_list=list(map(str,json3["matches"][str(match_name)]["bets"]))
                    outcomes=json3["outcomes"]
                    odds=json3["odds"]
                    bet_categories=json3["categories"]
                    bets = { key:value for (key,value) in json3["bets"].items() if key in bet_list}
                    #bets=json3["bets"]
                    bet_type=json3["filters"]
                except KeyError:
                    print("KeyError")
                    continue
                except AttributeError:
                    print("AttributeError")
                    continue
                except TypeError:
                    print("TypeError")
                    continue
                
                
                    
                
                ii=iter(bets.values())
                for i in ii:
                    try :
                        main_bet=i
                        #print(main_bet["betTitle"])
                        if main_bet["betTitle"] not in type_bets:
                            type_bets[main_bet["betTitle"]] = {outcomes[str(outcome)]["label"] : str(odds[str(outcome)]) for outcome in main_bet["outcomes"]}
                            #print("new")
                        else :
                            type_bets[main_bet["betTitle"]].update({outcomes[str(outcome)]["label"] : str(odds[str(outcome)]) for outcome in main_bet["outcomes"]})
                    except StopIteration:
                        print("error stop iteration")
                        continue
                    finally:
                        #print(i["betTitle"])
                        if "gameScore" in json3["matches"][str(match_name)].keys():
                            type_bets["gameScore"]=json3["matches"][str(match_name)]["gameScore"]
                        if "setScores" in json3["matches"][str(match_name)].keys():
                            type_bets["Score"]=json3["matches"][str(match_name)]["setScores"]
                        elif "score" in json3["matches"][str(match_name)].keys():
                            type_bets["Score"]=json3["matches"][str(match_name)]["score"]
                            
                time_stamp=datetime.datetime.today().time()
                #print(time_stamp)
                if json3["matches"][str(match_name)]["title"] not in list(self.dico.keys()):
                    try:    
                        self.dico[json3["matches"][str(match_name)]["title"]]={str(time_stamp.hour)+"h"+str(time_stamp.minute)+"."+str(time_stamp.second):type_bets}
                    except KeyError:
                        print("WTF")
                        pass
                else :
                    try:
                        self.dico[json3["matches"][str(match_name)]["title"]].update({str(time_stamp.hour)+"h"+str(time_stamp.minute)+"."+str(time_stamp.second):type_bets})
                    except KeyError:
                        self.dico[json3["matches"][str(match_name)]["title"]]={str(time_stamp.hour)+"h"+str(time_stamp.minute)+"."+str(time_stamp.second):type_bets}
        
                try:
                    if json3["matches"][str(match_name)]["remainingTime"].split(":")[0]<"02:30":
                        send_telegram_alert(json3["matches"][str(match_name)]["title"]+" termine bientôt",self.sport)
                except KeyError:
                    print("KeyError termine bientot")
                    pass
                except AttributeError:
                    pass
                
                try:
                    if self.verbose:
                        print(json3["matches"][str(match_name)]["setScores"])
                    #EVALUATE SURBETS HERE
                    try:
                        try:
                            dico_pre=self.dico_pre[json3["matches"][str(match_name)]["title"]]
                        except KeyError:
                            dico_pre=self.dico_pre[json3["matches"][str(match_name)]["title"]]
                        
                        
                        if json3["matches"][str(match_name)]["title"] not in self.track_record.keys():
                            self.track_record[json3["matches"][str(match_name)]["title"]]={"surebet":99}
                            
                        
                        j1,j2=type_bets["Vainqueur"]
                        if float(dico_pre["Vainqueur"][j1])>float(dico_pre["Vainqueur"][j2]):
                            a=float(dico_pre["Vainqueur"][j1])
                            surebet=round(calcul_surebet(a,float(type_bets["Vainqueur"][j2])),2)
                            mise=round(self.mise_base*a/float(type_bets["Vainqueur"][j2]),2)
                            if surebet<1:
                                pass
                            else :
                                if self.track_record[json3["matches"][str(match_name)]["title"]]["surebet"]==surebet:
                                    pass
                                else:
                                    send_telegram_alert("{} at {} \n Surebet = {} \n Mise ={}".format(j2,float(type_bets["Vainqueur"][j2]),surebet,mise),self.sport)
                            self.track_record.update({json3["matches"][str(match_name)]["title"]:{"surebet":surebet}})  
                        else :
                            a=float(dico_pre["Vainqueur"][j2])
                            surebet=round(calcul_surebet(a,float(type_bets["Vainqueur"][j1])),2)
                            mise=round(self.mise_base*a/float(type_bets["Vainqueur"][j1]),2)
                            if surebet<1.05 and surebet>0.92:
                                pass
                            else :
                                 if self.track_record[json3["matches"][str(match_name)]["title"]]["surebet"]==surebet:
                                    pass
                                 else:
                                     send_telegram_alert("{} at {} \n Surebet = {} \n Mise ={}".format(j1,float(type_bets["Vainqueur"][j1]),surebet,mise),self.sport)
                            
                            self.track_record.update({json3["matches"][str(match_name)]["title"]:{"surebet":surebet}})
                    except:
                        pass
                     
            
                except KeyError:
                    print("KeyError Scores")
                    try:
                        if self.verbose:
                            print(json3["matches"][str(match_name)]["score"])
                        try:
                            try:
                                dico_pre=self.dico_pre[json3["matches"][str(match_name)]["title"]]
                            except KeyError:
                                dico_pre=self.dico_pre[json3["matches"][str(match_name)]["title"]]
                                
                            j1,j2=type_bets["Vainqueur"]
                            if float(dico_pre["Vainqueur"][j1])>float(dico_pre["Vainqueur"][j2]):
                                a=float(dico_pre["Vainqueur"][j1])
                                surebet=round(calcul_surebet(a,float(type_bets["Vainqueur"][j2])),2)
                                mise=round(a/float(type_bets["Vainqueur"][j2]),2)
                                if surebet<1.05 :
                                    pass
                                else :
                                    send_telegram_alert("{} at {} \n Surebet = {} \n Mise ={}".format(j2,float(type_bets["Vainqueur"][j2]),surebet,mise),self.sport)
                                    
                            else :
                                a=float(dico_pre["Vainqueur"][j2])
                                surebet=round(calcul_surebet(a,float(type_bets["Vainqueur"][j1])),2)
                                mise=round(a/float(type_bets["Vainqueur"][j1]),2)
                                if surebet<1.05:
                                    pass
                                else :
                                    send_telegram_alert("{} at {} \n Surebet = {} \n Mise ={}".format(j1,float(type_bets["Vainqueur"][j1]),surebet,mise),self.sport)
                        except:
                            pass
                        
                    except KeyError:
                        print("KeyError final")
                        continue
            print(c)
            time.sleep(random.randint(self.pause,self.pause+5))
            
    def get_prematch(self):
        response = requests.get(self.sport_url, headers=self.headers)
        #response = requests.get(self.sport_url)
        html = response.text
        split1 = html.split("var PRELOADED_STATE = ")[1]
        split2 = split1.split(";</script>")[0]
        json2 = json.loads(split2)
        today = datetime.datetime.today() + datetime.timedelta(hours=+12)
        # recuperation des ids des matchs de la soirée uniquement (les matches qui sont dans maximum 12h (ligne precedente))
        self.id_list = {key:val for key, val in json2["matches"].items() if val["sportId"] == int(dico_sports[self.sport]["sport_id"]["Winamax"]) and val["status"] == "PREMATCH" and val["matchStart"] <= today.timestamp()}
        starting_matches=[i["matchStart"] for i in self.id_list.values()]
        
        #recup des cotes pour tous les matchs 
        #bets_matches_pre={}
        for match_name in self.id_list.keys():
            type_bets={}
            url="https://www.winamax.fr/paris-sportifs/match/"+str(match_name)
            #response = requests.get(url, headers=self.headers)
            response = requests.get(url, headers=self.headers)
            html = response.text
            split11 = html.split("var PRELOADED_STATE = ")[1]
            split22 = split11.split(";</script>")[0]
            
            json3 = json.loads(split22)
            bet_list=list(map(str,json3["matches"][str(match_name)]["bets"]))
            outcomes=json3["outcomes"]
            odds=json3["odds"]
            bet_categories=json3["categories"]
            bets = { key:value for (key,value) in json3["bets"].items() if key in bet_list}
            #bets=json3["bets"]
            bet_type=json3["filters"]
        
            ii=iter(json3["bets"].values())
            c=1
            for i in ii:
                try :
                    c+=1
                    main_bet=i
                    print(main_bet["betTitle"])
                    if main_bet["betTitle"] not in type_bets:
                        type_bets[main_bet["betTitle"]] = {outcomes[str(outcome)]["label"] : str(odds[str(outcome)]) for outcome in main_bet["outcomes"]}
                        #print("new")
                    else :
                        type_bets[main_bet["betTitle"]].update({outcomes[str(outcome)]["label"] : str(odds[str(outcome)]) for outcome in main_bet["outcomes"]})
                        for outcome in main_bet["outcomes"]:
                            print(outcomes[str(outcome)]["label"]+" : "+str(odds[str(outcome)]))
                except StopIteration:
                    break
            time.sleep(random.randint(2,4))

            self.dico[json3["matches"][str(match_name)]["title"]]=type_bets
    
    def scrap_live_forced(self):
                try:
                    self.scrape_live()
                except IndexError:
                    randomtime = random.randint(120,180)
                    print('ERROR - Retrying again website {} retrying in {} secs'.format(self.sport_url, randomtime))
                    self.save_data()
                    time.sleep(randomtime)
                    self.scrape_live()
                except ConnectionError as e:
                    print("Connection error:", e)
                    randomtime = random.randint(120,180)
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
