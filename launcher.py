# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 16:58:29 2024

@author: axel4
"""

from live_scrapping_manager import * 
import os

type_scrap=os.environ["TYPE_SCRAP"]
sport_name=os.environ["SPORT_NAME"]
bookmaker=os.environ["BOOKMAKER"]

if bookmaker=="Winamax":
    test=Winamax(sport=sport_name,type_scrap=type_scrap,mise_base=1,headless=False,date=datetime.date.today())
else:
    pass
test.load_data()
try :
    test.scrape()
finally:
    test.save_data2()
    print(str(datetime.datetime.now()))
