import json
import requests
import re
import time as t

from openrgb import OpenRGB
from bs4 import BeautifulSoup
from openrgb.utils import pack_color
from openrgb.consts import ORGBDeviceType
from datetime import datetime, time

prevPrice = 0
thisPrice = 0
#update this URL to change stocks
stonksURL = "https://www.google.com/finance/quote/GME:NYSE"
divName = 'div.YMlKec.fxKbKc'
pollDelay = 20

down = pack_color((255, 0, 0))
up = pack_color((0, 255, 0))
equal = pack_color((0, 0, 255))
client = OpenRGB('localhost', 6742)


#allows for checking the times to determine if it's the aftermarket or not
def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time
        
#scrapes the main website
def Scrape():
    page = requests.get(stonksURL)
    soup = BeautifulSoup(page.content, 'html.parser')
    prices = soup.select(divName)
    
    index = 1
    stringName = 'aftermarket'
    if is_time_between(time(14,30), time(21,00)):
        index = 0
        stringName = 'normal market'
    currentPrice = re.sub('[!@#$]', '', prices[index].text)

    print('{} in the {} is at {}'.format(datetime.now().strftime("%H:%M:%S"), stringName, currentPrice))
    return float(currentPrice)

#functions for setting the colors of all devices

def SetColor(color):
    for thing in client.devices():
        thing.set(color)
        
def PreCheck():
    print("Checking colors...")
    print("Green")
    SetColor(up)
    t.sleep(2)
    print("Red")
    SetColor(down)
    t.sleep(2)
    print("Blue")
    SetColor(equal)
    t.sleep(2)

#the main loop
def ActualLoop():
    PreCheck()
    prevPrice = Scrape()
    while(True):
        thisPrice = Scrape()
        if thisPrice < prevPrice:
            SetColor(down)
            print('Value went down from {} to {}'.format(prevPrice, thisPrice))
        elif thisPrice == prevPrice:
            SetColor(equal)
            print('Value is the same from {} to {}'.format(prevPrice, thisPrice))
        else:
            SetColor(up)
            print('Value went up from {} to {}'.format(prevPrice, thisPrice))
        prevPrice = thisPrice
        t.sleep(pollDelay)
        
ActualLoop()
    
    
