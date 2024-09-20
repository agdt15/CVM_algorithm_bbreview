# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 21:47:03 2023

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
#from selenium.webdriver.support.relative_locator import locate_with
from selenium.common.exceptions import TimeoutException

from odds_scrapper4 import *



class Betclic(OddsScraper):
    def __init__(self,sport,type_scrap,mise_base,date,delta=0,verbose=False):
        self.sport=sport
        self.date=date
        self.bookmaker="betclic"
        self.type_scrap=type_scrap
        self.sport_url = "https://www.betclic.fr/"+str(dico_sports[sport]["sport_id"]["Betclic"])
        self.pause=dico_sports[sport]["pause"]
        self.data="./Data/"+self.sport+"/data_"+self.sport.lower()+"_"+self.type_scrap+"_"+self.bookmaker+"_"+str(self.date+datetime.timedelta(hours=+delta)).replace("-","")+".pkl"
        self.data2="./Data/"+self.sport+"/data_"+self.sport.lower()+"_"+self.type_scrap+"_"+self.bookmaker+"_"+str(self.date+datetime.timedelta(hours=+24+delta)).replace("-","")+".pkl"
        
        #self.headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        self.headers=generate_random_headers()
        self.mise_base=mise_base
        self.verbose=verbose
        
    def scrape_live(self,surbet=False):
        #LOAD PRE LIVE ODDS
        if self.date!=datetime.date.today() :
            print("Attention date choisie non à jour, on garde bien la date actuelle pour les données live mais le calcul des surbets ne sera pas possible !")
            return 1
        
        a_file_pre = open("./Data/"+self.sport+"/data_"+self.sport.lower()+"_pre_"+self.bookmaker+"_"+str(datetime.date.today()).replace("-","")+".pkl", "rb")
        self.dico_pre=pickle.load(a_file_pre)
        a_file_pre.close()
        
        if(len(self.dico_pre)>0):
            self.dico_pre=self.dico_pre[list(self.dico_pre.keys())[-1]]
                
        #LAUNCH betclic SESSION
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        #driver = webdriver.Chrome()
        driver.get(self.sport_url)

        c=0
        time.sleep(1)
        #CLICK BUTTON COOKIES
        try:
             WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID,'popin_tc_privacy_button_3'))).click()
        except:
            pass
        finally:
            soup3=bs(driver.page_source, 'lxml')
            matches_lives=soup3.select("a.cardEvent.is-live")
            
            while len(matches_lives)>0:
                a, b = 1, 1
                c += 1
                print(c)
                if c % 3 == 0:
                    driver.get(self.sport_url)
                    try:
                         WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID,'popin_tc_privacy_button_3'))).click()
                    except:
                        pass
                    finally:
                        soup3=bs(driver.page_source, 'lxml')
                        matches_lives=soup3.select("a.cardEvent.is-live")
                elif c % 10 ==0 :
                    print("save data")
                    self.save_data()
                elif c%20==0:
                    driver.close()
                    driver = webdriver.Chrome(options=chrome_options)
                    try:
                         WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID,'popin_tc_privacy_button_3'))).click()
                    except:
                        pass
                        
                
                for i in matches_lives:
                    #get scores 
                    try:
                        scores=i.find("div",{"class":"scoreboard_tableBody"}).findAll("scoreboards-scoreboard-periods-scores")
                        scores_e1=[s.text.strip() for s in scores[0].findAll("span",{"class":"scoreboard_tableCell"})]
                        scores_e2=[s.text.strip() for s in scores[1].findAll("span",{"class":"scoreboard_tableCell"})]
                    except:
                        scores=i.find("div",{"class":"scoreboard_totalScore"})
                        scores_e1=[s.text.strip() for s in scores.findAll("span")[0]]
                        scores_e2=[s.text.strip() for s in scores.findAll("span")[1]]
                    #attention premier est le nom d'équipe et le dernier scoreboard_tableCell est le total
                    
                    
                    #dico pour contenir les cotes
                    type_bets = {}
                    
                    #aller au détail pour chaque match
                    driver.get("https://www.betclic.fr"+i.get("href"))
                
                    #toggle more jusqu'a la fin
                    try:
                        
                        l2 = driver.find_elements(By.CLASS_NAME, "isSeeMore")
                        ## click button
                        for j in l2:
                            driver.execute_script("arguments[0].click();", j);
                    except:
                        pass
                    
                    try:
                        soup_bet=bs(driver.page_source, 'lxml')
                        bets=soup_bet.findAll("sports-markets-single-market")
                    except KeyError:
                        print("keyerror")
                        continue
                    except AttributeError:
                        print("Attribute Error")
                        continue
                    except TimeoutException:
                        print("Timeout exception")
                        continue
                            
                    #NOM DU MATCH
                    match_name=scores_e1[0]+" - "+scores_e2[0]
                    
                    for bet in bets:
                        for classes in ["marketBox_headTitle ng-star-inserted","marketBox_headTitle","marketBox_lineSelection","marketBox_lineSelection ng-star-inserted"]:
                            try:
                                if bet.find("h2",{"class":classes}) is not None:
                                    main_bet=bet.find("h2",{"class":classes}).text.strip()
                                    #if self.verbose:
                                    #    print(main_bet)
                                    #for j in bet.findAll("div",{"class":"marketBox_lineSelection ng-star-inserted"}):
                                    #    print(j.text.strip().split("\n")[0]+" : "+re.search(r"[0-9]+\,[0-9]+$",j.text.strip())[0])
                                    if main_bet not in type_bets:
                                        
                                        if len(bet.findAll("p",{"class":"marketBox_label"})) == 0:
                                            
                                            type_bets[main_bet]={label.text.strip(): re.search(r"[0-9]+\,[0-9]{2}|[0-9]+$", odd.text.strip().replace("\n", "")).group(0).replace(",", ".") for label, odd in zip(bet.findAll("span", {"class":"is-top"}),[element for element in bet.findAll("span",{"class":"btn_label"}) if not element.find("span",{"style":""})] )}

                                        else :
                                            type_bets[main_bet] = {label.text.strip() : re.search(r"[0-9]+\,[0-9]{2}|[0-9]+$",odd.text.strip().replace("\n",""))[0].replace(",",".")  for label, odd in zip(bet.findAll("p",{"class":"marketBox_label"}),bet.findAll("span",{"class":"btn_label"})  ) }

                                        #print("new")
                                    else :
                                        if len(bet.findAll("p",{"class":"marketBox_label"})) == 0:
                                            
                                            type_bets[main_bet].update({label.text.strip(): re.search(r"[0-9]+\,[0-9]{2}|[0-9]+$", odd.text.strip().replace("\n", "")).group(0).replace(",", ".") for label, odd in zip(bet.findAll("span", {"class":"is-top"}),[element for element in bet.findAll("span",{"class":"btn_label"}) if not element.find("span",{"style":""})] )})

                                        else :
                                            type_bets[main_bet].update({label.text.strip() : re.search(r"[0-9]+\,[0-9]{2}|[0-9]+$",odd.text.strip().replace("\n",""))[0].replace(",",".")  for label, odd in zip(bet.findAll("p",{"class":"marketBox_label"}),bet.findAll("span",{"class":"btn_label"})  ) })

                                    break
                                else:
                                    pass
                            except StopIteration:
                                print("error stop iteration")
                                continue
                            except TypeError:
                                print(bet.findAll("h2"))
                                continue
                            finally:
                                pass
                           
                    type_bets["Score"]=" ".join([i+"-"+j for i,j in zip(scores_e1[1:-1],scores_e2[1:-1])])
                    time_stamp=datetime.datetime.today().time()
                    if match_name not in list(self.dico.keys()):
                        try:    
                            self.dico[match_name]={str(time_stamp.hour)+"h"+str(time_stamp.minute)+"."+str(time_stamp.second):type_bets}
                        except KeyError:
                            self.dico[match_name]={str(time_stamp.hour)+"h"+str(time_stamp.minute)+"."+str(time_stamp.second):type_bets}
                    else :
                        try:
                            self.dico[match_name].update({str(time_stamp.hour)+"h"+str(time_stamp.minute)+"."+str(time_stamp.second):type_bets})
                        except KeyError:
                            self.dico[match_name]={str(time_stamp.hour)+"h"+str(time_stamp.minute)+"."+str(time_stamp.second):type_bets}


                    if surbet:
                        try:
                            dico_pre=self.dico[match_name]
                            
                            if match_name not in self.track_record.keys():
                                self.track_record[match_name]={"surebet":99}
                                
                            
                            j1,j2=type_bets["Vainqueur"]
                            if float(dico_pre["Vainqueur"][j1]["odds"])>float(dico_pre["Vainqueur"][j2]["odds"]):
                                a=float(dico_pre["Vainqueur"][j1]["odds"])
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
                                a=float(dico_pre["Vainqueur"][j2]["odds"])
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
                        except:
                            pass
                time.sleep(dico_sports[self.sport]["pause"])
                        
                        
    def get_prematch(self):
        #LAUNCH betclic SESSION https://www.betclic.fr/football-s1/ligue-des-nations-uefa-c22676/france-belgique-m3002529585
        chrome_options = Options()
        #chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        #driver.get("https://www.betclic.fr/tennis-s2")
        driver.get(self.sport_url)
        
        time.sleep(1)
        #CLICK BUTTON COOKIES
        try:
             WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID,'popin_tc_privacy_button_3'))).click()
        except:
            pass
        finally:
            time.sleep(10)
            #SCROLLING INFINI
            ###############################################################################
            scroll_to_endpage(driver=driver, SCROLL_PAUSE_TIME=4)
            ###############################################################################
            soup3=bs(driver.page_source, 'lxml')
            #Pour lister tous les evenements qui ne sont pas en live
            self.id_list=soup3.select("a.cardEvent:not(.is-live)")
            #print(matches)
            
            if self.id_list:
                for i in self.id_list:
                    #get scores 
                    teams=[j.text.strip() for j in i.findAll("div",{"class":"scoreboard_contestantLabel"})]
                    if len(teams)<2:
                        continue
                    
                    #NOM DU MATCH
                    match_name=teams[0]+" - "+teams[1]
                    #dico pour contenir toutes les cotes (au travers de tous les onglets possibles pour la rencontre)
                    all_bets = {}
    
                    #aller au détail pour chaque match
                    driver.get("https://www.betclic.fr"+i.get("href"))
                                                
                    # Clicker sur toutes les toggles voir plus
                    try:
                        l2 = driver.find_elements(By.CLASS_NAME, "isSeeMore")
                        ## click button
                        for j in l2:
                            time.sleep(0.5)
                            driver.execute_script("arguments[0].click();", j);
                    except:
                        pass
                     
                    # Recupérer tous les onglets d'un match : par defaut -> le top 
                    soup_bet=bs(driver.page_source, 'lxml')
                    #Scoreboard info 
                    scoreboard_info=soup_bet.find("div",{"class":"scoreboard_info"})
                    match_date=scoreboard_info.find("div",{"class":"scoreboard_date"}).text.strip()
                    try :
                        match_start_hour=scoreboard_info.find("div",{"class":"scoreboard_hour"}).text.strip()
                    except:
                        print(match_name)
                        print("no hour")
                    
                    
                    # Formattage de la date 
                    if match_date=="":
                        match_date = datetime.date.today()
                    elif match_date=="Demain":
                        match_date = datetime.date.today() + datetime.timedelta(days=1)
                    elif match_date=="Après-demain":
                        match_date = datetime.date.today() + datetime.timedelta(days=2)
                    else:
                        match_date = dateparser.parse(match_date).date()
                    
                    list_tab=driver.find_elements(By.CSS_SELECTOR, "#matchHeader > div > sports-category-filters > bcdk-tabs > div > div > div > div.tab_item")
                    onglets_bets=[]
                    
                    if list_tab:
                        for j in list_tab:
                             time.sleep(0.5)
                             driver.execute_script("arguments[0].click();", j);
                             try:
                                 time.sleep(10)
                                 bets=bs(driver.page_source, 'lxml').findAll("sports-markets-single-market")
                                 onglets_bets.append(bets)
                             except KeyError:
                                 print("Key Error")
                                 continue
                             except AttributeError:
                                 print("Attribute Error")
                                 continue
                    else:
                        bets=bs(driver.page_source, 'lxml').findAll("sports-markets-single-market")
                        onglets_bets.append(bets)
                        
                     
                    for data_bets_onglet in onglets_bets :
                        type_bets = {}
                        for bet in data_bets_onglet:
                            try:
                                main_bet=bet.find("h2",{"class":"marketBox_headTitle"}).text.strip()
                                #print(main_bet)
                                try:
                                    if main_bet not in type_bets:
                                        
                                        if len(bet.findAll("p",{"class":"marketBox_label"})) == 0 and len([val.get("style") for val in bet.findAll('div',{"class":"progressBar_fill"})])==0:
                                            
                                            type_bets[main_bet]={label.text.strip(): {"odds":re.search(r"[0-9]+\,[0-9]{2}|[0-9]+$", odd.text.strip().replace("\n", "")).group(0).replace(",", ".")} for label, odd in zip(bet.findAll("span", {"class":"is-top"}),[element for element in bet.findAll("span",{"class":"btn_label"}) if not element.find("span",{"style":""})] )}
        
                                        elif  len(bet.findAll("p",{"class":"marketBox_label"})) == 0 and  len([val.get("style") for val in bet.findAll('div',{"class":"progressBar_fill"})])>0 :
                                            
                                            type_bets[main_bet]={label.text.strip(): {"odds":re.search(r"[0-9]+\,[0-9]{2}|[0-9]+$", odd.text.strip().replace("\n", "")).group(0).replace(",", "."), "percentDistribution":pct_bar} for label, odd, pct_bar in zip(bet.findAll("span", {"class":"is-top"}),[element for element in bet.findAll("span",{"class":"btn_label"}) if not element.find("span",{"style":""})],[val.get("style").split("width: ")[-1].replace(';','') for val in bet.findAll('div',{"class":"progressBar_fill"})] )}
                                        elif len(bet.findAll("p",{"class":"marketBox_label"})) > 0 and len([val.get("style") for val in bet.findAll('div',{"class":"progressBar_fill"})])==0 :
                                            type_bets[main_bet] = {label.text.strip() : {"odds":re.search(r"[0-9]+\,[0-9]{2}|[0-9]+$", odd.text.strip().replace("\n", "")).group(0).replace(",", ".")}  for label, odd in zip(bet.findAll("p",{"class":"marketBox_label"}),bet.findAll("span",{"class":"btn_label"})  ) }
                                        
                                        elif len(bet.findAll("p",{"class":"marketBox_label"})) > 0 and len([val.get("style") for val in bet.findAll('div',{"class":"progressBar_fill"})]) > 0 :
                                            type_bets[main_bet] = {label.text.strip() : {"odds":re.search(r"[0-9]+\,[0-9]{2}|[0-9]+$",odd.text.strip().replace("\n",""))[0].replace(",","."), "percentDistribution":pct_bar}  for label, odd, pct_bar in zip(bet.findAll("p",{"class":"marketBox_label"}),bet.findAll("span",{"class":"btn_label"},[val.get("style").split("width: ")[-1].replace(';','') for val in bet.findAll('div',{"class":"progressBar_fill"})])  ) }
                                        
                                        else:
                                            print("new")
                                    else :
                                       if len(bet.findAll("p",{"class":"marketBox_label"})) == 0 and len([val.get("style") for val in bet.findAll('div',{"class":"progressBar_fill"})])==0:
                                           
                                           type_bets[main_bet].update({label.text.strip(): {"odds":re.search(r"[0-9]+\,[0-9]{2}|[0-9]+$", odd.text.strip().replace("\n", "")).group(0).replace(",", ".")} for label, odd in zip(bet.findAll("span", {"class":"is-top"}),[element for element in bet.findAll("span",{"class":"btn_label"}) if not element.find("span",{"style":""})] )})
       
                                       elif  len(bet.findAll("p",{"class":"marketBox_label"})) == 0 and  len([val.get("style") for val in bet.findAll('div',{"class":"progressBar_fill"})])>0 :
                                           
                                           type_bets[main_bet].update({label.text.strip(): {"odds":re.search(r"[0-9]+\,[0-9]{2}|[0-9]+$", odd.text.strip().replace("\n", "")).group(0).replace(",", "."), "percentDistribution":pct_bar} for label, odd, pct_bar in zip(bet.findAll("span", {"class":"is-top"}),[element for element in bet.findAll("span",{"class":"btn_label"}) if not element.find("span",{"style":""})],[val.get("style").split("width: ")[-1].replace(';','') for val in bet.findAll('div',{"class":"progressBar_fill"})] )})
                                       elif len(bet.findAll("p",{"class":"marketBox_label"})) > 0 and len([val.get("style") for val in bet.findAll('div',{"class":"progressBar_fill"})])==0 :
                                           type_bets[main_bet].update({label.text.strip() : {"odds":re.search(r"[0-9]+\,[0-9]{2}|[0-9]+$", odd.text.strip().replace("\n", "")).group(0).replace(",", ".")}  for label, odd in zip(bet.findAll("p",{"class":"marketBox_label"}),bet.findAll("span",{"class":"btn_label"})  ) })
                                       
                                       elif len(bet.findAll("p",{"class":"marketBox_label"})) > 0 and len([val.get("style") for val in bet.findAll('div',{"class":"progressBar_fill"})]) > 0 :
                                           type_bets[main_bet].update({label.text.strip() : {"odds":re.search(r"[0-9]+\,[0-9]{2}|[0-9]+$",odd.text.strip().replace("\n",""))[0].replace(",","."), "percentDistribution":pct_bar}  for label, odd, pct_bar in zip(bet.findAll("p",{"class":"marketBox_label"}),bet.findAll("span",{"class":"btn_label"},[val.get("style").split("width: ")[-1].replace(';','') for val in bet.findAll('div',{"class":"progressBar_fill"})])  ) })
                                       
                                       else:
                                           print("new")
                                except:
                                    print("pb scrapping")
                                finally:
                                    pass
                            except StopIteration:
                                print("error stop iteration")
                                continue
                        all_bets.update(type_bets)
                        
                    all_bets["Date"]=match_date
                    self.dico[match_name]=all_bets
                    time.sleep(10)
                
                driver.close()
                print("Fin du scrapping")
                #FIN SCRAPPING 
                
                #TRI ET SAVE PAR DATE 
                dico_dates={}
                if len(self.dico):
                    for match_name, match_data in self.dico.items():
                        try : 
                            print(match_name)
                            print(match_data)
                            
                            # Extraire la date du dictionnaire match_data
                            date_element = match_data["Date"]
                          
                            # Créer un dictionnaire pour stocker les matchs par date (si ce n'est pas déjà fait)
                            if date_element not in dico_dates:
                                dico_dates[date_element] = {}
                          
                            # Ajouter le match actuel au dictionnaire pour la date correspondante
                            dico_dates[date_element][match_name] = match_data
                            self.dico_dates=dico_dates
                            self.dates=list(dico_dates.keys())
                        except:
                            print(match_name)
                            continue
                else:
                    self.dates=[]
            else:
                self.dates=[]
                
                
    
    def scrap_live_forced(self):
        try:
            self.scrape_live()
        except TimeoutException:
            randomtime = random.randint(60,500)
            print('ERROR - Retrying again website {} retrying in {} secs'.format(self.sport_url, randomtime))
            self.save_data()
            time.sleep(randomtime)
            self.scrape_live()
        except IndexError:
            randomtime = random.randint(60,500)
            print('ERROR - Retrying again website {} retrying in {} secs'.format(self.sport_url, randomtime))
            self.save_data()
            time.sleep(randomtime)
            self.scrape_live()
        except ConnectionError as e:
            print("Connection error:", e)
            randomtime = random.randint(60,500)
            print('ERROR - Retrying again website {}, retrying in {} secs'.format(self.sport_url, randomtime))
            self.save_data()
            time.sleep(randomtime)
            self.scrape_live()
        except requests.exceptions.Timeout as e:
            print("Timeout error:", e)
            randomtime = random.randint(60,500)
            print('ERROR - Retrying again website {}, retrying in {} secs'.format(self.sport_url, randomtime))
            self.save_data()
            time.sleep(randomtime)
            self.scrape_live()
        except requests.exceptions.RequestException as e:
            print("Error:", e)
            randomtime = random.randint(60,500)
            print('ERROR - Retrying again website {}, retrying in {} secs'.format(self.sport_url, randomtime))
            self.save_data()
            time.sleep(randomtime)
            self.scrape_live()
        except Exception as e:
            print("Error:", e)
            randomtime = random.randint(60,500)
            print('ERROR - Retrying again website {}, retrying in {} secs'.format(self.sport_url, randomtime))
            self.save_data()
            time.sleep(randomtime)
            self.scrape_live()
            
        finally:
            pass
                
    def scrape(self):
        if self.type_scrap=="live":
            self.scrap_live_forced()
                
        elif self.type_scrap=="pre":
            self.get_prematch()
    
                    
                    
