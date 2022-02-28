from discord.ext import commands
import time
import os

bot = commands.Bot(command_prefix = 'fa.')

async def check_logs():
    channel = bot.get_channel(941035604064473168)
    lm_channel = bot.get_channel(947656476711858176)
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
                for d in lines:
                    if d != '': 
                        await lm_channel.send(d)
    except FileNotFoundError:
        pass

@bot.command(name = 'run')
async def start_check(ctx):
    while True:
        await check_logs()
        time.sleep(10)

bot.run('OTQxMDMzMjUxMjE5MzIwODky.YgQDgg.6iNzsLYDiAAH7d4Vp8RUCrRbahU')