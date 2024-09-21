# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 22:02:54 2023

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

import os
import dateparser

is_git = True


#PARAMS

dico_sports = {"Basket":{"sport_id":{"Winamax":"2","Unibet":"basketball","Betclic":"basket-ball-s4"},"dico_pre":"data_basket_pre_unibet","dico_live":"data_basket_live_unibet","pause":15,"token":"5930848243:AAFSlGL5lsw0oeCPsrHRNgUMfkEWndZ4LyY"},
             "Baseball":{"sport_id":{"Winamax":"3","Unibet":"baseball","Betclic":"baseball-s20"},"dico_pre":"data_baseball_pre_unibet","dico_live":"data_baseball_live_unibet","pause":60,"token":"5989482610:AAFKFlc_I7-Se1ODV5ID5l9HtRmviIa8ulg"},
             "Hockey":{"sport_id":{"Winamax":"4","Unibet":"hockey-sur-glace","Betclic":"hockey-sur-glace-s13"},"dico_pre":"data_hockey_pre_unibet","dico_live":"data_hockey_live_unibet","pause":30,"token":"5960668232:AAEA5-uvTFXckL_fKiThfNjiLFpMgCPt1x4"},
             "Tennis": {"sport_id":{"Winamax":"5","Unibet":"tennis","Betclic":"tennis-s2"},"dico_pre":"data_tennis_pre_unibet","dico_live":"data_tennis_live2","pause":10,"token":"6050535846:AAHd0fXx7gi7kNJ2K9f0U8ynJcKMJWmOo7I"}
             ,"Rugby": {"sport_id":{"Winamax":"12","Unibet":"rugby-15","Betclic":"rugby-a-xv-s5"},"dico_pre":"data_rugby_pre_unibet","dico_live":"data_rugby_live_unibet","pause":60,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
,"NFL": {"sport_id":{"Winamax":"16","Unibet":"foot-americain/nfl","Betclic":"football-americain-s14"},"dico_pre":"data_nfl_pre","dico_live":"data_nfl_live","pause":60,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
,"Snooker": {"sport_id":{"Winamax":"19","Unibet":"snooker","Betclic":"basket-ball-s4"},"dico_pre":"data_snooker_pre","dico_live":"data_snooker_live","pause":60,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
,"Volley": {"sport_id":{"Winamax":"23","Unibet":"volleyball","Betclic":"volley-ball-s8"},"dico_pre":"data_volley_pre","dico_live":"data_volley_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
,"Beach Volley": {"sport_id":{"Winamax":"34","Unibet":"beach-volley","Betclic":"beach-volley-s49"},"dico_pre":"data_beach_volley_pre","dico_live":"data_beach_volley_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
,"Badminton": {"sport_id":{"Winamax":"31","Unibet":"badminton","Betclic":"badminton-s27"},"dico_pre":"data_badminton_pre","dico_live":"data_badminton_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
,"Handball": {"sport_id":{"Winamax":"6","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_handball_pre","dico_live":"data_handball_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},
"MMA": {"sport_id":{"Winamax":"117","Unibet":"mma","Betclic":"mma-s23"},"dico_pre":"data_mma_pre","dico_live":"data_mma_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},
"Ping Pong": {"sport_id":{"Winamax":"20","Unibet":"tennis-de-table","Betclic":"tennis-de-table-s32"},"dico_pre":"data_ping_pong_pre","dico_live":"data_ping_pong_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},
"Football": {"sport_id":{"Winamax":"1","Unibet":"football","Betclic":"football-s1"},"dico_pre":"data_football_pre","dico_live":"data_football_live","pause":60,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},
"Cyclisme": {"sport_id":{"Winamax":"17","Unibet":"cyclisme","Betclic":"cyclisme-s6"},"dico_pre":"data_cyclisme_pre","dico_live":"data_cyclisme_live","pause":60,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
}

"""
dico_jo = {
"Athletisme": {"sport_id":{"Winamax":"30/229","Unibet":"basketball","Betclic":"basket-ball-s4"},"dico_pre":"data_athletisme_pre_unibet","dico_live":"data_athletisme_live_unibet","pause":15,"token":"5930848243:AAFSlGL5lsw0oeCPsrHRNgUMfkEWndZ4LyY"},
"Aviron":{"sport_id":{"Winamax":"30/514","Unibet":"basketball","Betclic":"basket-ball-s4"},"dico_pre":"data_aviron_pre_unibet","dico_live":"data_aviron_live_unibet","pause":15,"token":"5930848243:AAFSlGL5lsw0oeCPsrHRNgUMfkEWndZ4LyY"},
"Basketball JO":{"sport_id":{"Winamax":"30/217","Unibet":"baseball","Betclic":"baseball-s20"},"dico_pre":"data_basketball_jo_pre_unibet","dico_live":"data_basketball_jo_live_unibet","pause":15,"token":"5989482610:AAFKFlc_I7-Se1ODV5ID5l9HtRmviIa8ulg"},
"Basketball_3_vs_3":{"sport_id":{"Winamax":"30/800000559","Unibet":"baseball","Betclic":"baseball-s20"},"dico_pre":"data_basketball_3_vs_3_jo_pre_unibet","dico_live":"data_basketball_3_vs_3_jo_live_unibet","pause":15,"token":"5989482610:AAFKFlc_I7-Se1ODV5ID5l9HtRmviIa8ulg"},
"Beach Volley JO": {"sport_id":{"Winamax":"30/230","Unibet":"beach-volley","Betclic":"beach-volley-s49"},"dico_pre":"data_beach_volley_jo_pre","dico_live":"data_beach_volley_jo_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},
"Boxe": {"sport_id":{"Winamax":"30/219","Unibet":"beach-volley","Betclic":"beach-volley-s49"},"dico_pre":"data_boxe_jo_pre","dico_live":"data_boxe_jo_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Canoe-Kayak":{"sport_id":{"Winamax":"30/524","Unibet":"hockey-sur-glace","Betclic":"hockey-sur-glace-s13"},"dico_pre":"data_canoe_kayak_pre_unibet","dico_live":"data_canoe_kayak_live_unibet","pause":30,"token":"5960668232:AAEA5-uvTFXckL_fKiThfNjiLFpMgCPt1x4"},

"Equitation":{"sport_id":{"Winamax":"30/515","Unibet":"hockey-sur-glace","Betclic":"hockey-sur-glace-s13"},"dico_pre":"data_equitation_pre_unibet","dico_live":"data_equitation_live_unibet","pause":30,"token":"5960668232:AAEA5-uvTFXckL_fKiThfNjiLFpMgCPt1x4"},

"Escalade":{"sport_id":{"Winamax":"30/800001079","Unibet":"hockey-sur-glace","Betclic":"hockey-sur-glace-s13"},"dico_pre":"data_escalade_pre_unibet","dico_live":"data_escalade_live_unibet","pause":30,"token":"5960668232:AAEA5-uvTFXckL_fKiThfNjiLFpMgCPt1x4"},

"Escrime":{"sport_id":{"Winamax":"30/236","Unibet":"hockey-sur-glace","Betclic":"hockey-sur-glace-s13"},"dico_pre":"data_escrime_pre_unibet","dico_live":"data_escrime_live_unibet","pause":30,"token":"5960668232:AAEA5-uvTFXckL_fKiThfNjiLFpMgCPt1x4"},

"Football JO": {"sport_id":{"Winamax":"30/221","Unibet":"football","Betclic":"football-s1"},"dico_pre":"data_football_jo_pre","dico_live":"data_football_jo_live","pause":60,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Golf JO": {"sport_id":{"Winamax":"30/1087","Unibet":"football","Betclic":"football-s1"},"dico_pre":"data_golf_jo_pre","dico_live":"data_golf_jo_live","pause":60,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Halterophilie": {"sport_id":{"Winamax":"30/235","Unibet":"football","Betclic":"football-s1"},"dico_pre":"data_halterophilie_pre","dico_live":"data_halterophilie_live","pause":60,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Handball JO": {"sport_id":{"Winamax":"30/222","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_handball_jo_pre","dico_live":"data_handball_jo_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Hockey sur gazon": {"sport_id":{"Winamax":"30/843","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_hockey_sur_gazon_pre","dico_live":"data_hockey_sur_gazon_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Judo": {"sport_id":{"Winamax":"30/231","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_judo_pre","dico_live":"data_judo_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Lutte": {"sport_id":{"Winamax":"30/521","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_lutte_pre","dico_live":"data_lutte_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Natation": {"sport_id":{"Winamax":"30/223","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_natation_pre","dico_live":"data_natation_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Pentathlon": {"sport_id":{"Winamax":"30/530","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_pentathlon_pre","dico_live":"data_pentathlon_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Rugby à 7": {"sport_id":{"Winamax":"30/1361","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_rugby_a_7_pre","dico_live":"data_rugby_a_7_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Taekwondo": {"sport_id":{"Winamax":"30/517","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_taekwondo_pre","dico_live":"data_taekwondo_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Tennis JO": {"sport_id":{"Winamax":"30/519","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_tennis_jo_pre","dico_live":"data_tennis_jo_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Tennis de table JO": {"sport_id":{"Winamax":"30/532","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_tennis_de_table_jo_pre","dico_live":"data_tennis_de_table_jo_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Tir": {"sport_id":{"Winamax":"30/520","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_tir_pre","dico_live":"data_tir_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Tir à l'arc": {"sport_id":{"Winamax":"30/237","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_tir_a_l_arc_pre","dico_live":"data_tir_a_l_arc_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Triathlon": {"sport_id":{"Winamax":"84","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_triathlon_pre","dico_live":"data_triathlon_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Voile": {"sport_id":{"Winamax":"81","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_voile_pre","dico_live":"data_voile_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Volley JO": {"sport_id":{"Winamax":"23","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_volley_jo_pre","dico_live":"data_volley_jo_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Water-Polo": {"sport_id":{"Winamax":"26","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_waterpolo_pre","dico_live":"data_waterpolo_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Badminton JO": {"sport_id":{"Winamax":"30/233","Unibet":"badminton","Betclic":"badminton-s27"},"dico_pre":"data_badminton_jo_pre","dico_live":"data_badminton_jo_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"},

"Cyclisme JO": {"sport_id":{"Winamax":"30/224","Unibet":"cyclisme","Betclic":"cyclisme-s6"},"dico_pre":"data_cyclisme_jo_pre","dico_live":"data_cyclisme_jo_live","pause":60,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}

}

dico_sports.update(dico_jo)
"""

def generate_random_headers():
    headers = {}
    user_agent = ''.join(random.choice(string.ascii_letters) for i in range(10))
    headers['User-Agent'] = user_agent
    accept_encoding = ['gzip, deflate', 'deflate, gzip', 'gzip', 'deflate']
    headers['Accept-Encoding'] = random.choice(accept_encoding)
    accept_language = ['en-US,en;q=0.5', 'en-US,en;q=0.8', 'en-US,en;q=0.3']
    headers['Accept-Language'] = random.choice(accept_language)
    return headers

def calcul_surebet(cote_a,cote_b):
    return 1/(1/cote_a+1/cote_b)
    
class OddsScraper():
        
    def load_data(self, ignore_dico2=False):
        try:
            a_file_pre = open(self.data, "rb")
            self.dico=pickle.load(a_file_pre)
            a_file_pre.close()
            print("\n")
            print("Load "+self.data+" file")  
        except FileNotFoundError:
            self.dico={}
        
        if ignore_dico2 is False:
            try:
                a_file_pre2 = open(self.data2, "rb")
                self.dico2=pickle.load(a_file_pre2)
                a_file_pre2.close()
                print("\n")
                print("Load "+self.data2+" file")  
            except FileNotFoundError:
                self.dico2={}
            
            
    def save_data(self, ignore_dico2=False):
        a_file_pre = open(self.data, "wb")
        pickle.dump(self.dico,a_file_pre)
        a_file_pre.close()
        print("\n")
        print("Save "+self.data+" file")
        
        if ignore_dico2 is False:
            a_file_pre2 = open(self.data2, "wb")
            pickle.dump(self.dico2,a_file_pre2)
            a_file_pre2.close()
            print("\n")
            print("Save "+self.data2+" file")
        
        
    def save_data2(self):
        
        if self.type_scrap=="live":
            a_file_pre = open(self.data, "wb")
            pickle.dump(self.dico,a_file_pre)
            a_file_pre.close()
            print("\n")
            print("Save "+self.data+" file")
            
            a_file_pre2 = open(self.data2, "wb")
            pickle.dump(self.dico2,a_file_pre2)
            a_file_pre2.close()
            print("\n")
            print("Save "+self.data2+" file")
            
        elif self.type_scrap=="pre":
            
            if self.bookmaker == "unibet" or self.bookmaker =="winamax" or self.bookmaker=="betclic":
                if len(self.dates):
                    for date_matches in self.dates:
                        date_data_path="./Data/"+self.sport+"/data_"+self.sport.lower()+"_"+self.type_scrap+"_"+self.bookmaker+"_"+str(date_matches).replace("-","")+".pkl"
                        try:
                            if os.path.exists(date_data_path):
                                a_file_pre = open(date_data_path, "rb")
                                dico_save=pickle.load(a_file_pre)
                                a_file_pre.close()
                                print("\n")
                                print("Update "+date_data_path+" file")
                                dico_save.update({datetime.datetime.today().timestamp():self.dico_dates[date_matches]})
                                a_file_pre = open(date_data_path, "wb")
                                pickle.dump(dico_save,a_file_pre)
                                a_file_pre.close()
                                print("Update "+date_data_path+" file completed")
                            else:
                                dico_save={datetime.datetime.today().timestamp():self.dico_dates[date_matches]}
                                a_file_pre = open(date_data_path, "wb")
                                pickle.dump(dico_save,a_file_pre)
                                a_file_pre.close()
                                print("\n")
                                print("Save "+date_data_path+" file")
                            
                        except FileNotFoundError:
                            dico_save={datetime.datetime.today().timestamp():self.dico_dates[date_matches]}
                            a_file_pre = open(date_data_path, "wb")
                            pickle.dump(dico_save,a_file_pre)
                            a_file_pre.close()
                            print("\n")
                            print("Save "+date_data_path+" file")
                    """   
                    if not os.path.exists(self.data2):
                        a_file_pre2 = open(self.data2, "wb")
                        if self.dico2:
                            pickle.dump(self.dico2,a_file_pre2)
                        a_file_pre2.close()
                        print("\n")
                        print("Save "+self.data2+" file")
                    else:
                        pass
                    """
                  if is_git:
                    
                else:
                    print(f"No data for this sport at {self.bookmaker} as of today")
                        
                
            else:
                try:
                    if os.path.exists(self.data):
                        a_file_pre = open(self.data, "rb")
                        dico_save=pickle.load(a_file_pre)
                        a_file_pre.close()
                        print("\n")
                        print("Update "+self.data+" file")
                        dico_save.update({datetime.datetime.today().timestamp():self.dico})
                        a_file_pre = open(self.data, "wb")
                        pickle.dump(dico_save,a_file_pre)
                        a_file_pre.close()
                        print("Update "+self.data+" file completed")
                    else:
                        dico_save={datetime.datetime.today().timestamp():self.dico}
                        a_file_pre = open(self.data, "wb")
                        pickle.dump(dico_save,a_file_pre)
                        a_file_pre.close()
                        print("\n")
                        print("Save "+self.data+" file")
                    
                except FileNotFoundError:
                    dico_save={datetime.datetime.today().timestamp():self.dico}
                    a_file_pre = open(self.data, "wb")
                    pickle.dump(dico_save,a_file_pre)
                    a_file_pre.close()
                    print("\n")
                    print("Save "+self.data+" file")
                    
                finally:
                    if not os.path.exists(self.data2):
                        a_file_pre2 = open(self.data2, "wb")
                        pickle.dump(self.dico2,a_file_pre2)
                        a_file_pre2.close()
                        print("\n")
                        print("Save "+self.data2+" file")
                    else:
                        pass
        
    def calcul_surbet(cote_a,cote_b):
        return 1/(1/cote_a+1/cote_b)
        
    def commit_data(self):
      try:
        commit_message = f"Add {self.type_scrap} {self.sport} {self.bookmaker} in data (Iteration {self.c})"
        subprocess.run(["git", "add", self.data])
        subprocess.run(["git", "commit", "-m", commit_message])
        subprocess.run(["git", "pull", "origin", "main"])
        subprocess.run(["git", "push", "origin", "main"])
      
        print(f"Committed data to {self.data}")
      
      except Exception as e:
            print(f"Error committing data: {str(e)}")
   
    
    def generate_random_headers():
        headers = {}
        user_agent = ''.join(random.choice(string.ascii_letters) for i in range(10))
        headers['User-Agent'] = user_agent
        accept_encoding = ['gzip, deflate', 'deflate, gzip', 'gzip', 'deflate']
        headers['Accept-Encoding'] = random.choice(accept_encoding)
        accept_language = ['en-US,en;q=0.5', 'en-US,en;q=0.8', 'en-US,en;q=0.3']
        headers['Accept-Language'] = random.choice(accept_language)
        return headers
    
    
    def clean_dico_pre(date_ins, sport, bookmaker):
        #date_ins = datetime.datetime.strptime(str(datetime.datetime(2024, 5, 28)), "%Y-%m-%d %H:%M:%S").date()
        if bookmaker == "Winamax" :
            scrapping_object = Winamax(sport=sport, type_scrap="pre",mise_base=1, date=date_ins)
            
        elif bookmaker == "Unibet" :
            scrapping_object = Uniber(sport=sport, type_scrap="pre",mise_base=1, date=date_ins)
            
        elif bookmaker == "Betclic" :
            scrapping_object = Betclic(sport=sport, type_scrap="pre",mise_base=1, date=date_ins)
        
        else:
            pass

        scrapping_object.load_data(ignore_dico2=True)
        
        dico_pre_dirty = scrapping_object.dico
        
        if len(dico_pre_dirty) == 0:
            print(f'There is not data {date_ins} for {sport} at {bookmaker}.')
            dico_cleaned = {}
        elif len(dico_pre_dirty) == 1 :
            ddd = scrapping_object.dico[0]
            dico_cleaned = {key:value for key, value in ddd.items() if type(key) is not float}
            #SAVE / REMOVE DATA 
        else :
            
            dico_cleaned={}
            timestamps=list(dico_pre_dirty.keys())
            for i, timestamp in enumerate(timestamps):
                dico_cleaned[timestamp]={key:value for key, value in scrapping_object.dico[timestamp].items() if type(key) is not float}
                
        return dico_cleaned
    
    
    
def scroll_to_endpage(driver, SCROLL_PAUSE_TIME = 0.5):
    #On doit scroller jusqu'a la fin de la page pour charger toutes les données
    #ce script permet de faire un scroll vers la fin de page (infini si besoin, utilisable pour insta ou linkedin)
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

        
