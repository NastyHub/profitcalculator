import json
import requests
import discord
from discord.ext import commands, tasks

req = requests.Session()


client = commands.Bot(command_prefix = '!')
client.remove_command('help')

def checkforopen():
    with open("profit.json") as f:
        jsondata = json.load(f)
        f.close()
    
    deallist = jsondata["deals"]
    deallist.reverse()

    for i in deallist:
        mynewlist = i 
        break
    
    if mynewlist["dealno"] == 0:
        return True, 1
    else:
        getcurrentnumber = mynewlist["dealno"]
        getnewnumber = getcurrentnumber + 1
        if mynewlist["done"] == True:
            return True, getnewnumber
        else:
            return False, getcurrentnumber, mynewlist

def checkopenorder(nameoftheorder):
    with open("order.json") as f:
        jsondata = json.load(f)
        f.close()
    
    orderlist = jsondata["orders"]

    for i in orderlist:
        #print(len(orderlist), i["ordername"], i["finished"])
        if i["ordername"] == nameoftheorder and i["finished"] == False:
            hit = True
            break
        else:
            hit = False
        
    if hit == False:
        return True, jsondata
    else:
        return False, i
            

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
    game = discord.Game(name = "calc")
    await client.change_presence(activity = game)
    updatecurrency.start()

@tasks.loop(seconds=86400)
async def updatecurrency():
    r = req.get("https://api.manana.kr/exchange/rate/KRW/KRW,USD,JPY.json").json()

    usdcurrency = round(r[1]["rate"])
    with open("profit.json") as f:
        jsondata = json.load(f)
        f.close()
    jsondata["rate"] = usdcurrency
    with open("profit.json", "w") as f:
        json.dump(jsondata, f, indent=2)
        f.close()
    
    print(f"Updated Currency to {usdcurrency}")

@client.command()
async def makeslot(ctx, *, description=None):

    if description != None:
        with open("profit.json") as f:
            jsondata = json.load(f)
            f.close()

        result = checkforopen()
        if result[0] == False:

            prettyprint = json.dumps(result[2], indent=2)
            
            await ctx.reply(f"There's already an open slot!\nTransaction No. {result[1]}\nData: ```json\n{prettyprint}```\nPlease use `!finishslot` to end this slot", mention_author=False)
        else:
            format = {
            "dealno": result[1],
            "desc": description,
            "sent": None,
            "received": None,
            "profitnumero": None,
            "profitpercentage": None,
            "done": False
            }

            jsonlist = jsondata["deals"]
            jsonlist.append(format)

            with open("profit.json", "w") as f:
                json.dump(jsondata, f, indent=2)
                f.close()
            
            await ctx.reply(f"A new slot has been made.```json\n{json.dumps(format, indent=2)}```\nYou may now adjust the values using `!sent`, `!received`", mention_author=False)

    else:
        await ctx.reply("Please add a description to help you remember details about this transaction later on!\n`!makeslot Classic Fedora`", mention_author=False)

@client.command()
async def finishslot(ctx):
    result = checkforopen()
    if result[0] == True:
        await ctx.reply("There isn't an open slot. Perhaps trying creating a slot with `!makeslot`?", mention_author=False)
    else:
        jsonlist = result[2]
        currentnumber = result[1]
        if jsonlist["sent"] != None and jsonlist["received"] != None:
            with open("profit.json") as f:
                jsondata = json.load(f)
                f.close()
            
            Totaldeal = jsondata["TotalDeals"]
            Totaldeal += 1
            
            jsondata["TotalDeals"] = Totaldeal

            for i in jsondata["deals"]:
                if i["dealno"] == currentnumber:
                    i["done"] = True
                    break
            
            with open("profit.json", "w") as f:
                json.dump(jsondata, f, indent=2)
                f.close()
            
            await ctx.reply(f"Successfully finished Transaction No. {currentnumber}", mention_author=False)
        else:
            await ctx.reply(f"The slot isn't able to wrap up. Please fill out the 'sent' and 'received' section or if you want to terminate this slot, please use `!abortslot`", mention_author=False)

@client.command()
async def abortslot(ctx):
    result = checkforopen()
    if result[0] == True:
        await ctx.reply("There isn't an open slot. Perhaps trying creating a slot with `!makeslot`?", mention_author=False)
    else:
        currentnumber = result[1]
        with open("profit.json") as f:
            jsondata = json.load(f)
            f.close()

        for i in jsondata["deals"]:
            if i["dealno"] == currentnumber:
                jsondata["deals"].remove(i)
                break

        print(jsondata)
        
        with open("profit.json", "w") as f:
            json.dump(jsondata, f, indent=2)
            f.close()
            
            await ctx.reply(f"Successfully deleted Transaction No. {currentnumber}", mention_author=False)

@client.command()
async def sent(ctx, money=None):
    if money == None:
        await ctx.send("Please add money value to the command. `!sent 45.8`(USD currency)")
    else:
        result = checkforopen()
        if result[0] == True:
            await ctx.reply("There isn't an open slot. Perhaps trying creating a slot with `!makeslot`?", mention_author=False)
        else:
            currentnumber = result[1]

            with open("profit.json") as f:
                jsondata = json.load(f)
                f.close()
            
            rate = jsondata["rate"]

            try:
                realmoney = round(float(money))
                total = round(realmoney*rate)
            
                Totaldeal = jsondata["TotalDeals"]
                Totaldeal += 1
                
                jsondata["TotalDeals"] = Totaldeal
                
                for i in jsondata["deals"]:
                    if i["dealno"] == currentnumber:
                        i["sent"] = total
                        break
                
                with open("profit.json", "w") as f:
                    json.dump(jsondata, f, indent=2)
                    f.close()

                await ctx.reply(f"Successful:\nUSD: {money}\nKRW: {total}", mention_author=False)

            except:
                await ctx.reply(f"error: likely that the value wasn't a number.", mention_author=False)
                
@client.command()
async def received(ctx, money=None):
    if money == None:
        await ctx.send("Please add money value to the command. `!received 5000`(KRW currency)")
    else:
        result = checkforopen()
        if result[0] == True:
            await ctx.reply("There isn't an open slot. Perhaps trying creating a slot with `!makeslot`?", mention_author=False)
        else:
            jsonlist = result[2]

            if jsonlist["sent"] == None:
                await ctx.reply("Please use the `!sent USD` command first", mention_author=False)
            else:
                currentnumber = result[1]

                with open("profit.json") as f:
                    jsondata = json.load(f)
                    f.close()

                Totaldeal = jsondata["TotalDeals"]
                Totaldeal += 1
                
                jsondata["TotalDeals"] = Totaldeal

                try:
                    realmoney = round(float(money))
                
                    for i in jsondata["deals"]:
                        if i["dealno"] == currentnumber:
                            i["received"] = realmoney
                            break
                    
                    sentmoney = jsonlist["sent"]
                    receivedmoney = realmoney

                    profitnumero = receivedmoney - sentmoney
                    profitpercentage = round(profitnumero/sentmoney*100)

                    i["profitnumero"] = profitnumero
                    i["profitpercentage"] = profitpercentage
                    
                    with open("profit.json", "w") as f:
                        json.dump(jsondata, f, indent=2)
                        f.close()

                    await ctx.reply(f"Successful:\nSent: {sentmoney}원\nReceived: {receivedmoney}원\nProfitAmount: {profitnumero}원\nProfitPercentage: {profitpercentage}%", mention_author=False)

                except:
                    print("placeholder")

@client.command()
async def sendfile(ctx):
    await ctx.send(file=discord.File("profit.json"))
    #await ctx.send(file=discord.File("order.json"))

@client.command()
async def createorder(ctx, name=None, stock=None):
    if name == None:
        await ctx.send("Please add name value to the command. `!createorder nameoftheorder`")
    else:
        if stock == None:
            stock = 1
        else:
            try:
                stock = int(stock)
            except:
                stock = 1
        
        result = checkopenorder(name)

        if result[0] == True:
            format = {
            "ordername": name,
            "stocks": stock,
            "finished": False
            }

            jsondata = result[1]
            jsondata["orders"].append(format)

            with open("order.json", "w") as f:
                json.dump(jsondata, f, indent=2)
                f.close()

            prettyprint = json.dumps(format, indent=2)

            await ctx.reply(f"Successfully created an order: ```json\n{prettyprint}```", mention_author=False)

        else:
            prettyprint = json.dumps(result[1], indent=2)
            await ctx.reply(f"You already have an open order: ```json\n{prettyprint}```", mention_author=False)

@client.command()
async def addorder(ctx, name=None, stock=None):
    if name == None or stock == None:
        await ctx.send("Please add name and stock value to the command. `!addstock name stock`")
    else:
        stock = int(stock)

        result = checkopenorder(name)

        if result[0] == True:
            await ctx.reply(f"Order named `{name}` does not exist.", mention_author=False)
        else:
            orderlist = result[1]

            currentstock = orderlist["stocks"]

            newstock = currentstock + stock
            
            orderlist["stocks"] = newstock

            nameoftheorder = orderlist["ordername"]

            with open("order.json") as f:
                jsondata = json.load(f)
                f.close()

            for i in jsondata["orders"]:
                if i["ordername"] == nameoftheorder:
                    jsondata["orders"].remove(i)
                    
                    jsondata["orders"].append(orderlist)
                    break
                else:
                    pass

            with open("order.json", "w") as f:
                json.dump(jsondata, f, indent=2)
                f.close()
            
            prettyprint = json.dumps(orderlist, indent=2)

            await ctx.reply(f"Successfully added {stock} stock to `{name}`: ```json\n{prettyprint}```", mention_author=False)

@client.command()
async def finishorder(ctx, name=None, stock=None):
    if name == None or stock == None:
        await ctx.send("Please add name and stock value to the command. `!finishorder name stock`")
    else:
        stock = int(stock)

        result = checkopenorder(name)

        if result[0] == True:
            await ctx.reply(f"Order named `{name}` does not exist.", mention_author=False)
        else:
            orderlist = result[1]

            currentstock = orderlist["stocks"]

            if currentstock == stock:
                newstock = 0
                
                orderlist["stocks"] = 0
                orderlist["finished"] = True

                nameoftheorder = orderlist["ordername"]

                with open("order.json") as f:
                    jsondata = json.load(f)
                    f.close()

                for i in jsondata["orders"]:
                    if i["ordername"] == nameoftheorder:
                        jsondata["orders"].remove(i)
                        
                        jsondata["orders"].append(orderlist)
                        break
                    else:
                        pass

                with open("order.json", "w") as f:
                    json.dump(jsondata, f, indent=2)
                    f.close()
                
                prettyprint = json.dumps(orderlist, indent=2)

                await ctx.reply(f"Successfully finished an order: ```json\n{prettyprint}```", mention_author=False)

            elif currentstock > stock:
                orderlist = result[1]

                newstock = currentstock - stock

                orderlist["stocks"] = newstock

                nameoftheorder = orderlist["ordername"]

                with open("order.json") as f:
                    jsondata = json.load(f)
                    f.close()

                for i in jsondata["orders"]:
                    if i["ordername"] == nameoftheorder:
                        jsondata["orders"].remove(i)
                        
                        jsondata["orders"].append(orderlist)
                        break
                    else:
                        pass

                with open("order.json", "w") as f:
                    json.dump(jsondata, f, indent=2)
                    f.close()
                
                prettyprint = json.dumps(orderlist, indent=2)

                await ctx.reply(f"Successfully finished an order: ```json\n{prettyprint}```", mention_author=False)

            else:
                await ctx.reply(f"You originally had {currentstock} stocks. You can't remove {stock} due to the end result being minus.", mention_author=False)

client.run("ODczODYzMTE0NTQ4OTk4MTQ0.YQ-mcg.3ErcvT0ALvAZTkq7ZJZrF1YC3no")