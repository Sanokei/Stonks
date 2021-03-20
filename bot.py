import json
import wikipedia

from bs4 import BeautifulSoup
import requests
import sys
from datetime import datetime, timedelta
import pandas as pd

import discord
from discord.ext import commands
from discord import Colour
bot = discord.Client()
bot = commands.Bot(command_prefix='$')

import nest_asyncio 
nest_asyncio.apply()

class ConnectionIssueError(Exception):
    """Exception raised. Connection Issue resulted while searching."""

    def __init__(self, message="Connection Problems"):
        self.message = message
        super().__init__(self.message)
        
class NoTickerError(Exception):
    """This Ticker is non existant error"""
    
    def __init__(self,ticker,message="Ticker was not found in database"):
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.ticker}: {self.message}"
    
class CryptoFoundError(Exception):
    """This was detected as a crypto"""
    
    def __init__(self,ticker,message="was detected as a crypto please use $crypto"):
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.ticker}: {self.message}"

def get_sano_data(ticker):
    ticker = ticker.replace(" ","+")
    while True:
        url = "https://finance.yahoo.com/quote/{}".format(ticker)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'referer': 'https://finance.yahoo.com/lookup'}
        
        #Connection to website
        try:
            source = requests.get(url,headers=headers)
        except:
            raise ConnectionIssueError

        #Attaching BS4 to page
        soup = BeautifulSoup(source.text, 'lxml')

        #If it reconnects it means it doesnt know the ticker but is searching with yahoo lookup
        if source.history:
            try:
                if(not soup.find('a', attrs={"data-reactid": "32"}) == None):
                    raise NoTickerError(ticker)
            except:
                ticker = soup.find('a', attrs={"data-reactid": "57"}).findAll(text=True)[0]
        else:
            break
    
    #Tests if its a crypto or not
    try:
        if(soup.find('span', attrs={"data-reactid": "69"}).findAll(text=True)[0] == "Algorithm"):
            raise CryptoFoundError
    except:
        mainDic = {
            "Name":soup.find('h1',attrs={"data-reactid": "7"}).findAll(text=True)[0],
            "info":url,
            "Price":soup.find('span',attrs={"data-reactid": "50"}).findAll(text=True)[0],
            "Change":soup.find('span',attrs={"data-reactid": "51"}).findAll(text=True)[0]
        }
        tab_of_tabs = [soup.find('div', attrs={"data-test": "left-summary-table"}).findAll("tr"),soup.find('div', attrs={"data-test": "right-summary-table"}).findAll("tr")]
        payload = {}
        for tab in tab_of_tabs:
            for tr in tab:
                td = tr.findAll('td')
                payload[td[0].findAll(text=True)[0]] = td[1].findAll(text=True)[0]
            
    return {"main":mainDic,"payload":payload}

# ticker = "gme"
# url = "https://finance.yahoo.com/quote/{}".format(ticker)
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
#     'referer': 'https://finance.yahoo.com/lookup'}

# #Connection to website
# try:
#     source = requests.get(url,headers=headers)
# except:
#     raise ConnectionIssueError

# #Attaching BS4 to page
# soup = BeautifulSoup(source.text, 'lxml')
# mainDic = {"Name":soup.find('h1',attrs={"data-reactid": "7"}).findAll(text=True)[0],"info":url}
# tab_of_tabs = [soup.find('div', attrs={"data-test": "left-summary-table"}).findAll("tr"),soup.find('div', attrs={"data-test": "right-summary-table"}).findAll("tr")]
# payload = {}
# for tab in tab_of_tabs:
#     for tr in tab:
#         td = tr.findAll('td')
#         print(td[0].findAll(text=True)[0])
#         print(td[1].findAll(text=True)[0])

def get_website(name):
    url = "https://www.4search.com/search/?q={}".format(name.replace(" ","+"))
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'referer': 'https://www.4search.com/'}

    #Connection to website
    try:
        source = requests.get(url,headers=headers)
    except:
        raise ConnectionIssueError

    soup = BeautifulSoup(source.text, 'lxml')
    try:
        for card in soup.findAll('div',attrs={"class": "card"}):
            website = soup.findAll('p')[0].find('img',alt=True)['alt']

            if(website.count(".") == 2):
                compname = website.split('.', 1)[1].split('.')[0]
            else:
                compname = website.split('.', 1)[0]
            if(get_sano_data(name).get("main").get("Name") == get_sano_data(compname).get("main").get("Name")):
                return website
    except:
        return "unknown website"

def get_img(name):
    url = "https://www.4search.com/search/?q={}".format(name.replace(" ","+"))
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'referer': 'https://www.4search.com/'}

    #Connection to website
    try:
        source = requests.get(url,headers=headers)
    except:
        raise ConnectionIssueError

    soup = BeautifulSoup(source.text, 'lxml')
    try:
        for card in soup.findAll('div',attrs={"class": "card"}):
            website = soup.findAll('p')[0].find('img',alt=True)['alt']

            if(website.count(".") == 2):
                compname = website.split('.', 1)[1].split('.')[0]
            else:
                compname = website.split('.', 1)[0]
            if(name in get_sano_data(compname).get("main").get("Name")):
                return "https://logo.clearbit.com/{}".format(website)
    except:
        return "https://aliceasmartialarts.com/wp-content/uploads/2017/04/default-image.jpg"

# name = "game stop" 
# url = "https://www.4search.com/search/?q={}".format(name.replace(" ","+"))
# headers = {
# 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
# 'referer': 'https://www.4search.com/'}

# #Connection to website
# try:
#     source = requests.get(url,headers=headers)
# except:
#     raise ConnectionIssueError

# soup = BeautifulSoup(source.text, 'lxml')

# for card in soup.findAll('div',attrs={"class": "card"}):
#     website = soup.findAll('p')[0].find('img',alt=True)['alt']

#     if(website.count(".") == 2):
#         compname = website.split('.', 1)[1].split('.')[0]
#     else:
#         compname = website.split('.', 1)[0]
#     result = get_sano_data(compname)
#     print("Result: ",result)
#     if(name in result.get("main").get("Name")):
#         print(works)
    

# name = "GameStop Corp."
# url = "https://www.4search.com/search/?q={}".format(name.replace(" ","+"))
# headers = {
# 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
# 'referer': 'https://www.4search.com/'}

# #Connection to website
# try:
#     source = requests.get(url,headers=headers)
# except:
#     raise ConnectionIssueError

# soup = BeautifulSoup(source.text, 'lxml')
# try:
#     for card in soup.findAll('div',attrs={"class": "card"}):
#         website = soup.findAll('p')[0].find('img',alt=True)['alt']

#         if(website.count(".") == 2):
#             compname = website.split('.', 1)[1].split('.')[0]
#         else:
#             compname = website.split('.', 1)[0]
#         if(name in get_sano_data(compname).get("main").get("Name")):
#             return "https://logo.clearbit.com/{}".format(website)
# except:
#     return "https://aliceasmartialarts.com/wp-content/uploads/2017/04/default-image.jpg"

#image https://duckduckgo.com/?q={}&atb=v123-1&iax=images&ia=images
#return image link
'''
def get_logo(ticker:str):
    ticker = "gme"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    }
    url="https://clearbit.com/logo"

    img = soup.find('h1', attrs={"data-reactid": "7"}).findall('img').findAll(src=True)
    print(img)
'''

#log in message
@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name)
    print("ID: ", bot.user.id)
    print('------')

#stonks
@bot.command(aliases=['s','stocks','stonk'],name="stonks",description="Give stock price of specific stock")
async def stonks(ctx, *, message):
    message = message.lower()
    
    #easter egg
    if(message == "moon"):
        embeded = discord.Embed(title="You found a easter egg retard", description="WE ARE GOING TO THE MOON", color=0xff0000)
        embeded.set_thumbnail(url="https://cdn.discordapp.com/emojis/529104156955508736.png?v=1")
        await ctx.send(embed=embeded)
        return
    
    #Getting stonk info
    try:
        stonk_info_payload = get_sano_data(message.upper()) 
        stonk_info = stonk_info_payload.get("payload")
        stonk_info_main = stonk_info_payload.get("main")
    except:
        raise get_sano_data(message.upper()) 
    
    #Get wikipedia info
    try:
        wiki_info = wikipedia.summary(stonk_info_main.get("Name"), sentences=1)
    except:
        wiki_info = "No info found on wikipedia"

    ticker = message.upper()    
        
    #change color of embed based on positive or negative
    #TODO: add range of color based on how green or red
    #make into a function
    try:
        dollarChange = stonk_info_main.get("Change").split("(",1)[0]
        percentChange = stonk_info_main.get("Change").replace(dollarChange,"")
    except:
        print("")
    try:
        if(float(dollarChange) > 0):
            stonk_color = 0x0ac429
        elif(float(dollarChange) < 0):
            stonk_color = 0xc40a0a
        else:
            stonk_color = 0xbdbbbb
    except:
        stonk_color = 0xbdbbbb
    
    #create embed
    embeded = discord.Embed(title=stonk_info_main.get("Name")+' | '+stonk_info_main.get("Price")+" | "+stonk_info_main.get("Change"), description=wiki_info, color=stonk_color)
    for key in stonk_info.keys():
        embeded.add_field(name=key,value= stonk_info.get(key),inline=True)
    embeded.add_field(name="info",value= "[Scraped from Yahoo Finance]("+stonk_info_main.get("info")+")"+"["+stonk_info_main.get("Name").split("(",1)[0]+"]\n"+"("+get_website(stonk_info_main.get("Name").split("(",1)[0])+")\n"+"[Logos provided by Clearbit](https://clearbit.com)",inline=False)
    embeded.set_thumbnail(url=get_img(get_website(stonk_info_main.get("Name").split("(",1)[0])))
    await ctx.send(embed=embeded) 
    return

#Stonks Error handeling
@stonks.error
async def stonks_error(ctx, error):
    if(isinstance(error,NoTickerError)):
        embeded = discord.Embed(title="Please enter a valid stonk name", description="No stonk name or ticker detected", color=0xff0000)
        embeded.set_thumbnail(url="https://cdn.discordapp.com/emojis/635268683383701564.png?v=1")
        embeded.add_field(name="Example:",value="$stonks MOON",inline=False)
        embeded.add_field(name="Error:",value=error,inline=False)
        await ctx.send(embed=embeded)

'''@bot.command(aliases=['b','get','loadup','invest'],name="buy",description="Buy stonk at specific price")
async def buy(ctx, stonk: str, amount: int):
    '''

@bot.command(aliases=['j'],name="join",description="Join a started competition")
async def join(ctx,name):
    file_name = ".json"
    with open(file_name) as f:
        data = json.loads(f.read())

#Generic Error handeling
@bot.listen("on_command_error")
async def on_command_error(ctx, error):
    if(not isinstance(error,AttributeError)):
        embeded = discord.Embed(title="You are autistic", description="you fucked up big time buccko", color=0xff0000)
        embeded.set_thumbnail(url="https://cdn.discordapp.com/attachments/813920772456054834/814368900157276160/477926174518149120.png")
        embeded.add_field(name="idk how this happened tbh",value="For more infomation use the command $retarded, $autistic or $help",inline=True)
        embeded.add_field(name="Error:",value=error,inline=False)
        await ctx.send(embed=embeded)

bot.run("Discord API Key")
