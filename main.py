import json
import requests
import discord
from discord.ext import commands, tasks

req = requests.Session()


client = commands.Bot(command_prefix = '!')
client.remove_command('help')

'''
format2 =  { 
            "dealno" : 1,
            "sent" : 1000,
            "received" : 3000,
            "profitnumero" : 300,
            "profitpercentage" : 31
            }

with open("format.json") as f:
    jsondata = json.load(f)
    f.close()

jsonlist = jsondata["deals"]
jsonlist.append(format2)

with open("format.json", "w") as f:
    json.dump(jsondata, f, indent=2)
    f.close()
'''

@client.event
async def on_ready():
    print("Ready!")
    game = discord.Game(name = "리미티드 정보 훔치는중")
    await client.change_presence(activity = game)
    updatecurrency.start()

@tasks.loop(seconds=86400)
async def updatecurrency():
    r = req.get("https://api.manana.kr/exchange/rate/KRW/KRW,USD,JPY.json").json()

    usdcurrency = int(r[1]["rate"])
    with open("profit.json") as f:
        jsondata = json.load(f)
        f.close()
    jsondata["rate"] = usdcurrency
    with open("profit.json", "w") as f:
        json.dump(jsondata, f, indent=2)
        f.close()
    
    print(f"Updated Currency to {usdcurrency}")




client.run("ODczODYzMTE0NTQ4OTk4MTQ0.YQ-mcg.3ErcvT0ALvAZTkq7ZJZrF1YC3no")