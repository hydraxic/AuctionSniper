# -*- coding: utf-8 -*-

# modules

import asyncio
from json import JSONDecodeError
import re
import os, sys
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer
import time
import requests

# auction api

c = requests.get("https://api.hypixel.net/skyblock/auctions?page=0")
resp = c.json()
now = resp['lastUpdated']
toppage = resp['totalPages']

a_url = requests.get("https://moulberry.codes/lowestbin.json")
au = a_url.json()

# result and prices variables

results = []
lm_results = []
f3_results = []
pet_results = []
ignore_special_results = []
ignore_special_results_1m = []

prices = {}
prices_ignore_special = {}

# parts to remove

STARS = [" ✦", "⚚ ", " ✪", "✪"]
REFORGES = ["Very ",'Highly ','Extremely ','Not So ','Thicc ','Absolutely ','Even More ',"Stiff ", "Lucky ", "Jerry's ", "Dirty ", "Fabled ", "Suspicious ", "Gilded ", "Warped ", "Withered ", "Bulky ", "Stellar ", "Heated ", "Ambered ", "Fruitful ", "Magnetic ", "Fleet ", "Mithraic ", "Auspicious ", "Refined ", "Headstrong ", "Precise ", "Spiritual ", "Moil ", "Blessed ", "Toil ", "Bountiful ", "Candied ", "Submerged ", "Reinforced ", "Cubic ", "Warped ", "Undead ", "Ridiculous ", "Necrotic ", "Spiked ", "Jaded ", "Loving ", "Perfect ", "Renowned ", "Giant ", "Empowered ", "Ancient ", "Sweet ", "Silky ", "Bloody ", "Shaded ", "Gentle ", "Odd ", "Fast ", "Fair ", "Epic ", "Sharp ", "Heroic ", "Spicy ", "Legendary ", "Deadly ", "Fine ", "Grand ", "Hasty ", "Neat ", "Rapid ", "Unreal ", "Awkward ", "Rich ", "Clean ", "Fierce ", "Heavy ", "Light ", "Mythic ", "Pure ", "Smart ", "Titanic ", "Wise ", "Bizarre ", "Itchy ", "Ominous ", "Pleasant ", "Pretty ", "Shiny ", "Simple ", "Strange ", "Vivid ", "Godly ", "Demonic ", "Forceful ", "Hurtful ", "Keen ", "Strong ", "Superior ", "Unpleasant ", "Zealous ","Double-Bit ","Lumberjack's ","Great ","Rugged ","Lush ","Green Thumb ","Peasant's ","Robust ","Zooming ","Unyielding ","Prospector's ","Excellent ","Sturdy ","Fortunate ","Strengthened ","Fortified ","Waxed ","Glistening ","Treacherous ","Salty ","Candied "]

# reforge filters

SWORDFLIPREFORGES_Filter_I = ['Fabled', 'Withered', 'Suspicious']
ARMORFLIPREFORGES_Filter_I = ['Ancient', 'Renowned', 'Necrotic']

IGNOREARMOURS_Filter_LM = ['Glacite', 'Goblin', 'Crystal', 'Farm', 'Mushroom', 'Angler', 'Pumpkin', 'Cactus', 'Leaflet', 'Lapis', 'Miner\'s', 'Golem', 'Miner', 'Hardened Diamond', 'Fairy', 'Growth', 'Salmon', 'Zombie', 'Speedster', 'Holy', 'Rotten', 'Bouncy', 'Heavy', 'Skeleton Grunt', 'Skeleton Soldier', 'Super Heavy']

awmrf3r_withered_prelist = ['Flower of Truth', 'Livid Dagger', 'Shadow Fury', 'Emerald Blade', 'Giant\'s Sword', 'Soul Whip', 'Phantom Rod']
awmrf3r_fabled_prelist = ['Flower of Truth', 'Livid Dagger', 'Shadow Fury', 'Emerald Blade', 'Giant\'s Sword', 'Voidedge Katana', 'Reaper Falchion', 'Soul Whip',' Phantom Rod']

armour_weapon_meta_reforge_f3_remake = {
    #reforge, items
    'Withered': awmrf3r_withered_prelist,
    'Fabled': awmrf3r_fabled_prelist,
    'Giant': ['Goldor\'s', 'Reaper Mask', 'Necromancer Lord'],
    'Ancient': ['Necron\'s', 'Maxor\'s', 'Final Destination', 'Shadow Assassin', 'Tarantula', 'Superior', 'Golden Bonzo', 'Diamond Bonzo', 'Golden Scarf', 'Diamond Scarf', 'Golden Professor', 'Diamond Professor', 'Golden Thorn', 'Diamond Thorn', 'Golden Livid', 'Diamond Livid', 'Golden Sadan', 'Diamond Sadan', 'Golden Necron', 'Diamond Necron'],
    'Necrotic': ['Storm\'s', 'Necromancer Lord', 'Wither Goggles', 'Spirit Boots'],
    'Jaded': ['Sorrow', 'Divan\'s'],
    'Spiritual': ['Juju Shortbow'],
    'Renowned': ['Sorrow'],
}

ultimate_enchants = ['Bank V', 'Chimera V', 'Combo V', 'Duplex V', 'Fatal Tempo V', 'Flash V', 'Inferno V', 'Last Stand V', 'Legion V', 'No Pain No Gain V', 'One For All', 'Rend V', 'Soul Eater V', 'Swarm V', 'Ultimate Jerry V', 'Ultimate Wise V', 'Wisdom V']

ignore_reforges_f2 = {
    #swords
    'Gentle',
    'Odd',
    'Fast',
    'Fair',
    'Epic',
    'Sharp',
    'Heroic',
    'Spicy',
    'Legendary',
    #bows? maybe idk i see a lot of profitable flips with blacksmith reforges in bow section
    #armour
    'Clean',
    'Fierce',
    'Heavy',
    'Light',
    'Mythic',
    'Pure',
    'Smart',
    'Titanic',
    'Wise',
}

# the lowest price an item can have
LOWEST_PRICE = 500

# config variables
LOWEST_PERCENT_MARGIN = 1/2 # percent diffences for super sniper
LARGE_MARGIN_P_M = 0.9 # percent differences for filtered snipers
LARGE_MARGIN = 1000000 # flips that are more than a mil profit
LARGE_MARGIN_MAXCOST = 50000000 #50m
F3_MAXCOST = 200000000 #200m

START_TIME = default_timer()

def fetch(session, page):
    global toppage
    base_url = "https://api.hypixel.net/skyblock/auctions?page="
    with session.get(base_url + page) as response:
        # puts response in a dict
        try:
            data = response.json()
            toppage = data['totalPages']
            if data['success']:
                toppage = data['totalPages']
                for auction in data['auctions']:
                    if not auction['claimed'] and auction['bin'] == True and not "Furniture" in auction["item_lore"]: # if the auction isn't a) claimed and is b) BIN
                        # removes level if it's a pet, also
                        name = str(auction['item_name'])
                        tier = str(auction['tier'])
                        
                        if "Rune I" in auction["item_lore"]:
                            return
                        
                        index = re.sub("\[[^\]]*\]", "", name + tier)
                        # if the current item already has a price in the prices map, the price is updated
                        filtindex = index
                        for reforge in REFORGES:
                            if reforge in filtindex:
                                filtindex = filtindex.replace(reforge, "")
                            else:
                                filtindex = filtindex.replace(reforge, "")
                        for star in STARS:
                            if star in filtindex:
                                filtindex = filtindex.replace(star, "")
                            else:
                                filtindex = filtindex.replace(star, "")

                        
                        if index in prices:
                            if prices[index][0] > auction['starting_bid']:
                                prices[index][1] = prices[index][0]
                                prices[index][0] = auction['starting_bid']
                            elif prices[index][1] > auction['starting_bid']:
                                prices[index][1] = auction['starting_bid']
                        # otherwise, it's added to the prices map
                        else:
                            prices[index] = [auction['starting_bid'], float("inf")]

                        if filtindex in prices_ignore_special:
                            if prices_ignore_special[filtindex][0] > auction['starting_bid']:
                                prices_ignore_special[filtindex][1] = prices_ignore_special[filtindex][0]
                                prices_ignore_special[filtindex][0] = auction['starting_bid']
                            elif prices_ignore_special[filtindex][1] > auction['starting_bid']:
                                prices_ignore_special[filtindex][1] = auction['starting_bid']
                        else:
                            prices_ignore_special[filtindex] = [auction['starting_bid'], float("inf")]
                        
                        if prices_ignore_special[filtindex][1] > LOWEST_PRICE and prices_ignore_special[filtindex][0]/prices_ignore_special[filtindex][1] < LOWEST_PERCENT_MARGIN and auction['start'] + 60000 > now:
                            ignore_special_results.append([auction['uuid'], re.sub(tier, "", filtindex), auction['starting_bid'], filtindex])
                        if prices_ignore_special[filtindex][1] > LOWEST_PRICE and prices_ignore_special[filtindex][0]/prices_ignore_special[filtindex][1] < LARGE_MARGIN_P_M and prices_ignore_special[filtindex][1] - prices_ignore_special[filtindex][0] >= LARGE_MARGIN and auction['start'] + 60000 > now:
                            ignore_special_results_1m.append([auction['uuid'], re.sub(tier, "", filtindex), auction['starting_bid'], filtindex])                                                    # vv since f3_maxcost is larger than large_margin_maxcost, i can check to see if large_margin_maxcost within f3_maxcost
                        #$print(prices[index][1], prices[index][0], auction['start'] + 60000 - now)
                        if prices[index][1] > LOWEST_PRICE and prices[index][0]/prices[index][1] < LARGE_MARGIN_P_M and prices[index][1] - prices[index][0] >= LARGE_MARGIN and prices[index][0] <= F3_MAXCOST and auction['start'] + 60000 > now:
                          #  print('here2')
                            if prices[index][0] <= LARGE_MARGIN_MAXCOST:
                             #   print('here1')
                                if auction['category'] == 'weapon' or auction['category'] == 'armor':
                              #      print('here')
                                    desc = str(auction['item_lore'])
                                    global ult_ench
                                    global auprice
                                    global auformat
                                    ult_ench = None
                                    auprice = None
                                    auformat = None
                                    for ench in ultimate_enchants:
                                        if ench in desc:
                                            print("ench is in desc")
                                            ult_ench = ench
                                            if not ult_ench == 'One For All' and not ult_ench == 'Ultimate Wise V':
                                                print('ench is not ofa or uwv')
                                                auname = ult_ench.rsplit(' ', 1)[0]
                                                aunameCaps = auname.upper()
                                                aunameformat = aunameCaps.replace(' ', '_')
                                                auformat = 'ULTIMATE_{};5'.format(aunameformat)
                                            elif ult_ench == 'One For All':
                                                auformat = 'ULTIMATE_ONE_FOR_ALL;1'
                                            elif ult_ench == 'Ultimate Wise V':
                                                auformat = 'ULTIMATE_WISE;5'
                                    if auformat in au:
                                        print('auformat is in au')
                                        auprice = float(au[auformat])

                                    if auction['category'] == 'armor':
                                        ignore = False
                                        for name in IGNOREARMOURS_Filter_LM:
                                            if name in auction['item_name']:
                                                ignore = True
                                        if ignore == False:
                                            lm_results.append([auction['uuid'], re.sub(tier, "", index), auction['starting_bid'], index, [ult_ench, auprice]])
                                    if auction['category'] == 'weapon':
                                        lm_results.append([auction['uuid'], re.sub(tier, "", index), auction['starting_bid'], index, [ult_ench, auprice]])
                                if auction['category'] == 'misc':
                                    if 'Right-click to add this pet to' in auction['item_lore']:
                                        pet_results.append([auction['uuid'], re.sub(tier, "", index), auction['starting_bid'], index, [ult_ench, auprice]])
                            if prices[index][0] <= F3_MAXCOST:
                                if auction['category'] == 'weapon' or auction['category'] == 'armor':
                                    if auction['category'] == 'armor':
                                        ignore = False
                                        for name in IGNOREARMOURS_Filter_LM:
                                            if name in auction['item_name']:
                                                ignore = True
                                        if ignore == False:
                                            f3_results.append([auction['uuid'], re.sub(tier, "", index), auction['starting_bid'], index, [ult_ench, auprice]])
                                    if auction['category'] == 'weapon':
                                        f3_results.append([auction['uuid'], re.sub(tier, "", index), auction['starting_bid'], index, [ult_ench, auprice]])
            return data
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(e, exc_type, fname, exc_tb.tb_lineno)
            return

async def get_data_asynchronous():
    # puts all the page strings
    pages = [str(x) for x in range(toppage)]
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            START_TIME = default_timer()
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, page) # Allows us to pass in multiple arguments to `fetch`
                )
                # runs for every page
                for page in pages if int(page) < toppage
            ]
            for response in await asyncio.gather(*tasks):
                pass

def main():
    # Resets variables
    global results, lm_results, f3_results, prices, ignore_special_results, ignore_special_results_1m, prices_ignore_special, pet_results, START_TIME
    START_TIME = default_timer()
    results = []
    lm_results = []
    f3_results = []
    ignore_special_results = []
    ignore_special_results_1m = []
    pet_results = []
    prices = {}
    prices_ignore_special = {}
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_data_asynchronous())
    loop.run_until_complete(future)

    # Makes sure all the results are still up to date

    #main sniper gone cuz bad #2
    print(lm_results)
    #keeping just in case tho
    #if len(results): results = [[entry, prices[entry[3]][1]] for entry in results if (entry[2] > LOWEST_PRICE and prices[entry[3]][1] != float('inf') and prices[entry[3]][0] == entry[2] and prices[entry[3]][0]/prices[entry[3]][1] < LOWEST_PERCENT_MARGIN)]
    if len(lm_results): lm_results = [[entry, prices[entry[3]][1]] for entry in lm_results if (entry[2] > LOWEST_PRICE and prices[entry[3]][1] != float('inf') and prices[entry[3]][0] == entry[2] and prices[entry[3]][0]/prices[entry[3]][1] < LARGE_MARGIN_P_M and prices[entry[3]][1] - prices[entry[3]][0] >= LARGE_MARGIN and prices[entry[3]][0] <= LARGE_MARGIN_MAXCOST)]
    if len(f3_results): f3_results = [[entry, prices[entry[3]][1]] for entry in f3_results if (entry[2] > LOWEST_PRICE and prices[entry[3]][1] != float('inf') and prices[entry[3]][0] == entry[2] and prices[entry[3]][0]/prices[entry[3]][1] < LARGE_MARGIN_P_M and prices[entry[3]][1] - prices[entry[3]][0] >= LARGE_MARGIN and prices[entry[3]][0] <= F3_MAXCOST)]
    if len(ignore_special_results): ignore_special_results = [[entry, prices_ignore_special[entry[3]][1]] for entry in ignore_special_results if (entry[2] > LOWEST_PRICE and prices_ignore_special[entry[3]][1] != float('inf') and prices_ignore_special[entry[3]][0] == entry[2] and prices_ignore_special[entry[3]][0]/prices_ignore_special[entry[3]][1] < LOWEST_PERCENT_MARGIN)]
    if len(ignore_special_results_1m): ignore_special_results_1m = [[entry, prices_ignore_special[entry[3]][1]] for entry in ignore_special_results_1m if (entry[2] > LOWEST_PRICE and prices_ignore_special[entry[3]][1] != float('inf') and prices_ignore_special[entry[3]][0] == entry[2] and prices_ignore_special[entry[3]][0]/prices_ignore_special[entry[3]][1] < LARGE_MARGIN_P_M and prices_ignore_special[entry[3]][1] - prices_ignore_special[entry[3]][0] >= LARGE_MARGIN)]
    if len(pet_results): pet_results = [[entry, prices[entry[3]][1]] for entry in pet_results if (entry[2] > LOWEST_PRICE and prices[entry[3]][1] != float('inf') and prices[entry[3]][0] == entry[2] and prices[entry[3]][0]/prices[entry[3]][1] < LARGE_MARGIN_P_M and prices[entry[3]][1] - prices[entry[3]][0] >= LARGE_MARGIN and prices[entry[3]][0] <= LARGE_MARGIN_MAXCOST)]
    #print(pet_results)

    '''

    #main sniper gone cuz bad #3
    #keeping just in case
    if len(results): # if there's results to print
        for result in results:
            with open('./fliplogs/logs.txt', 'a') as fAp:
                toprint = "\nView Auction: " + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1])
                fAp.write(toprint)
                #fAp.close()
                #print(toprint)
        print("\nLooking for auctions...")

        '''
    
    #superfilter

    if len(ignore_special_results):
        for result in ignore_special_results:
            with open('./fliplogs/logs_s.txt', 'a') as fApSpecial:
                toprint = "\nView Auction: " + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1])
                fApSpecial.write(toprint)
                #fAp.close()
                #print(toprint)

    '''if len(ignore_special_results_1m):
        for result in ignore_special_results_1m:
            with open('./fliplogs/logs_s2.txt', 'a') as fApSpecial2:
                toprint = "\nView Auction: " + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1])
                fApSpecial2.write(toprint)'''

    ##ah-sniper-f1 and #ah-sniper-filtered

    if len(lm_results):
        for result in lm_results:
            #print(result)
            with open('./fliplogs/logs_f1.txt', 'a') as fAp2:
                if isinstance(result[0][4][0], str):
                    toprint = "\nView Auction: " + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1]) + " Ultimate Enchant: `{}` | Lowest BIN For Ultimate Enchant: `{}`".format(result[0][4][0], result[0][4][1])
                else:
                    toprint = "\nView Auction: " + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1])
                fAp2.write(toprint)
                #fAp.close()
                #print(toprint)
            with open('./fliplogs/logs_f2.txt', 'a') as fAp3:
                truechecker = []
                for reforge in ignore_reforges_f2:
                    if not str(result[0][1]).startswith(reforge):
                        truechecker.append(True)
                    else:
                        truechecker.append(False)
                if not False in truechecker:
                    if isinstance(result[0][4][0], str):
                        toprint = "\nView Auction: " + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1]) + " Ultimate Enchant: `{}` | Lowest BIN For Ultimate Enchant: `{}`".format(result[0][4][0], result[0][4][1])
                    else:
                        toprint = "\nView Auction: " + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1])
                    fAp3.write(toprint)
            with open('./fliplogs/logs_f2_2.txt', 'a') as fAp3_2:
                truechecker2 = []
                for reforge in ignore_reforges_f2:
                    if not str(result[0][1]).startswith(reforge) and ('✪' not in str(result[0][1]) or str(result[0][1]).count('✪') == 5):
                        truechecker2.append(True)
                    else:
                        truechecker2.append(False)
                if not False in truechecker2:
                    if isinstance(result[0][4][0], str):
                        toprint = "\nView Auction: " + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1]) + " Ultimate Enchant: `{}` | Lowest BIN For Ultimate Enchant: `{}`".format(result[0][4][0], result[0][4][1])
                    else:
                        toprint = "\nView Auction: " + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1])
                    fAp3_2.write(toprint)
            with open('./fliplogs/logs_f3.txt', 'a') as fAp4:
                for reforge, AorWs in armour_weapon_meta_reforge_f3_remake.items():
                    if reforge in str(result[0][1]) and any(substring in str(result[0][1]) for substring in AorWs) and ('✪' not in str(result[0][1]) or str(result[0][1]).count('✪') == 5):
                        if isinstance(result[0][4][0], str):
                            toprint = "\nView Auction: " + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1]) + " Ultimate Enchant: `{}` | Lowest BIN For Ultimate Enchant: `{}`".format(result[0][4][0], result[0][4][1])
                        else:
                            toprint = "\nView Auction: " + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1])
                        fAp4.write(toprint)
    
    if len(pet_results):
        for result in pet_results:
            with open('./fliplogs/pet_logs.txt', 'a') as fAp5:
                toprint = "\nView Auction: " + "/viewauction `" + str(result[0][0]) + "` | Item: `" + str(result[0][1]) + "` | Price: `{:,}`".format(result[0][2]) + " | Second Lowest BIN: `{:,}`".format(result[1])
                fAp5.write(toprint)

print("Looking for auctions...")
main()

def dostuff():
    global now, toppage

    # if 60 seconds have passed since the last update
    if time.time() * 1000 > now + 60000:
        prevnow = now
        now = float('inf')
        try:
            c = requests.get(
                "https://api.hypixel.net/skyblock/auctions?page=0")
            type = str(c.headers['Content-Type'])
            if c.ok and 'application/json; charset=utf-8' == type:
                try:
                    c = c.json()
                    if c:
                        if c['lastUpdated'] != prevnow:
                            now = c['lastUpdated']
                            toppage = c['totalPages']
                            main()
                        else:
                            now = prevnow
                            return
                except ValueError:
                    print('bad response')
                    os.execv(sys.executable, ['python'] + sys.argv)
            else:
                print('not json response')
                os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            print('uh oh error ' + str(e))
            os.execv(sys.executable, ['python'] + sys.argv)

while True:
    dostuff()
    time.sleep(0.25)
