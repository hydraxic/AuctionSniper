from discord.ext import commands
import time

bot = commands.Bot(command_prefix = 'fa.')

async def check_logs():
    channel = bot.get_channel(941035604064473168)
    log = './fliplogs/logs.txt'
    with open(log, 'r') as f:
        if f.read() != None:
            await channel.send(f.read())

@bot.command(name = 'run')
async def start_check(ctx):
    while True:
        await check_logs()
        time.sleep(10)

bot.run('OTQxMDMzMjUxMjE5MzIwODky.YgQDgg.6iNzsLYDiAAH7d4Vp8RUCrRbahU')