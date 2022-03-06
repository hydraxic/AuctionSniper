from discord.ext import commands
import time
import os
import collections

bot = commands.Bot(command_prefix = 'fa.')

def sort_margins(margins):
    sorted_dict_to_list = sorted(margins, key = lambda tup: tup[0], reverse=True)
    return sorted_dict_to_list

def get_margin(auctions):
    new_auction_list = {}
    for auc in auctions:
        if auc != '':
            pricei_i = auc.replace('`','')
            pricei_ii = pricei_i.split('Item price: ')[1]
            pricei_iii = pricei_ii.split(' | ')[0]
            pricei_iv = pricei_iii.replace(',','')
            pricei_v = int(pricei_iv)
            priceii_i = auc.replace('`','')
            priceii_ii = priceii_i.split('Item price: ')[1]
            priceii_iii = priceii_ii.split(' | Second lowest BIN: ')[1]
            priceii_iv = priceii_iii.replace(',','')
            priceii_v = int(priceii_iv)

            margin = (priceii_v - pricei_v)

            if margin <= 5000000:
                new_auction_list[margin] = auc
    if new_auction_list != {}: return new_auction_list

async def check_logs():
    channel = bot.get_channel(949012493047578624)
    lm_channel = bot.get_channel(949012556100554752)
    log = './logs.txt'
    lmlog = './logs_lm.txt'
    try:
        with open(log, 'r+') as f:
            if os.path.getsize('./logs.txt') > 0:
                lines = [line.rstrip() for line in f]
                for d in lines:
                    if d != '': 
                        await channel.send(d)
                f.truncate(0)
        with open(lmlog, 'r+') as f:
            if os.path.getsize('./logs_lm.txt') > 0:
                lines = [line.rstrip() for line in f]
                slist = sort_margins(get_margin(lines))
                await channel.purge(limit=5)
                flips10 = slist[:10]
                tosend = '\n'.join(flips10)
                await lm_channel.send(tosend)
    except FileNotFoundError:
        pass

@bot.command(name = 'run')
async def start_check(ctx):
    while True:
        await check_logs()
        time.sleep(10)

bot.run('OTQxMDMzMjUxMjE5MzIwODky.YgQDgg.6iNzsLYDiAAH7d4Vp8RUCrRbahU')