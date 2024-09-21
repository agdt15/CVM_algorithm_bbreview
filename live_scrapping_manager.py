# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 17:01:16 2023

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
from winamax import * 
from unibet import * 
from betclic import *

for sp in sorted(list(dico_sports.keys()), key=lambda x: random.random()):

    test_Winamax = Betclic(sport=sp, type_scrap="pre",
                           mise_base=1, delta=0, date=datetime.date.today())
    try:
        test_Winamax.scrape()
    except (KeyError,TypeError):
        print("attention on a eu un pb ici")
        continue
    except requests.exceptions.ConnectionError as e:
        print("Connection error:", e)
        pass
    except requests.exceptions.Timeout as e:
        print("Timeout error:", e)
        pass
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        pass
    except KeyboardInterrupt:
        pass
    finally:
        test_Winamax.save_data2()
