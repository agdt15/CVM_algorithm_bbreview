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
import subprocess




#PARAMS

dico_sports={"Basket":{"sport_id":{"Winamax":"2","Unibet":"basketball","Betclic":"basket-ball-s4"},"dico_pre":"data_basket_pre_unibet","dico_live":"data_basket_live_unibet","pause":15,"token":"5930848243:AAFSlGL5lsw0oeCPsrHRNgUMfkEWndZ4LyY"},
             "Baseball":{"sport_id":{"Winamax":"3","Unibet":"baseball","Betclic":"baseball-s20"},"dico_pre":"data_baseball_pre_unibet","dico_live":"data_baseball_live_unibet","pause":60,"token":"5989482610:AAFKFlc_I7-Se1ODV5ID5l9HtRmviIa8ulg"},
             "Hockey":{"sport_id":{"Winamax":"4","Unibet":"hockey-sur-glace","Betclic":"hockey-sur-glace-s13"},"dico_pre":"data_hockey_pre_unibet","dico_live":"data_hockey_live_unibet","pause":30,"token":"5960668232:AAEA5-uvTFXckL_fKiThfNjiLFpMgCPt1x4"},
             "Tennis": {"sport_id":{"Winamax":"5","Unibet":"tennis","Betclic":"tennis-s2"},"dico_pre":"data_tennis_pre_unibet","dico_live":"data_tennis_live2","pause":10,"token":"6050535846:AAHd0fXx7gi7kNJ2K9f0U8ynJcKMJWmOo7I"}
             ,"Football": {"sport_id":{"Winamax":"1","Unibet":"football","Betclic":"football-s1"},"dico_pre":"data_football_pre_unibet","dico_live":"data_football_live_unibet","pause":60,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
             ,"Rugby": {"sport_id":{"Winamax":"12","Unibet":"rugby-15","Betclic":"rugby-a-xv-s5"},"dico_pre":"data_rugby_pre_unibet","dico_live":"data_rugby_live_unibet","pause":60,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
,"NFL": {"sport_id":{"Winamax":"16","Unibet":"foot-americain/nfl","Betclic":"football-americain-s14"},"dico_pre":"data_nfl_pre","dico_live":"data_nfl_live","pause":60,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
,"Snooker": {"sport_id":{"Winamax":"19","Unibet":"snooker","Betclic":"basket-ball-s4"},"dico_pre":"data_snooker_pre","dico_live":"data_snooker_live","pause":60,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
,"Volley": {"sport_id":{"Winamax":"23","Unibet":"volleyball","Betclic":"volley-ball-s8"},"dico_pre":"data_volley_pre","dico_live":"data_volley_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
,"Beach Volley": {"sport_id":{"Winamax":"34","Unibet":"beach-volley","Betclic":"beach-volley-s49"},"dico_pre":"data_beach_volley_pre","dico_live":"data_beach_volley_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
,"Badminton": {"sport_id":{"Winamax":"31","Unibet":"badminton","Betclic":"badminton-s27"},"dico_pre":"data_badminton_pre","dico_live":"data_badminton_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
,"Handball": {"sport_id":{"Winamax":"6","Unibet":"handball","Betclic":"handball-s9"},"dico_pre":"data_handball_pre","dico_live":"data_handball_live","pause":20,"token":"6316873619:AAFww3QVt6XvLlDvEdSHFPt9Yt5Ux4myiIA"}
}

import os 
ids_telegram=[os.environ["ID_TELEGRAM"]]






def generate_random_headers():
    headers = {}
    user_agent = ''.join(random.choice(string.ascii_letters) for i in range(10))
    headers['User-Agent'] = user_agent
    accept_encoding = ['gzip, deflate', 'deflate, gzip', 'gzip', 'deflate']
    headers['Accept-Encoding'] = random.choice(accept_encoding)
    accept_language = ['en-US,en;q=0.5', 'en-US,en;q=0.8', 'en-US,en;q=0.3']
    headers['Accept-Language'] = random.choice(accept_language)
    return headers


def send_telegram_alert(text,sport,ids=ids_telegram):
    token = dico_sports[sport]["token"]
    url = f"https://api.telegram.org/bot{token}"
    message=text
    for id_x in ids:
        # params = {"chat_id": "5808361291", "text": message}
        params = {"chat_id": id_x, "text": message}
        r = requests.get(url + "/sendMessage", params=params)

    
def calcul_surebet(cote_a,cote_b):
    return 1/(1/cote_a+1/cote_b)
    
class OddsScraper():
        
    def load_data(self):
        try:
            a_file_pre = open(self.data, "rb")
            self.dico=pickle.load(a_file_pre)
            a_file_pre.close()
            print("\n")
            print("Load "+self.data+" file")  
        except FileNotFoundError:
            self.dico={}
        
        try:
            a_file_pre2 = open(self.data2, "rb")
            self.dico2=pickle.load(a_file_pre2)
            a_file_pre2.close()
            print("\n")
            print("Load "+self.data2+" file")  
        except FileNotFoundError:
            self.dico2={}
            
            
    def save_data(self):
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
        else:
            print("Not type scrap is odd")
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
        
    def calcul_surbet(cote_a,cote_b):
        return 1/(1/cote_a+1/cote_b)
        
        
    
    def generate_random_headers():
        headers = {}
        user_agent = ''.join(random.choice(string.ascii_letters) for i in range(10))
        headers['User-Agent'] = user_agent
        accept_encoding = ['gzip, deflate', 'deflate, gzip', 'gzip', 'deflate']
        headers['Accept-Encoding'] = random.choice(accept_encoding)
        accept_language = ['en-US,en;q=0.5', 'en-US,en;q=0.8', 'en-US,en;q=0.3']
        headers['Accept-Language'] = random.choice(accept_language)
        return headers
        
