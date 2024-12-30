import logging
import time

from discord.ext import commands
import discord
import os # default module
from dotenv import load_dotenv
from prometheus_client import Histogram

load_dotenv() # load all the variables from the env file
# bot = commands.Bot(debug_guilds=[1001916230069911703], intents=discord.Intents.all())
bot = commands.Bot(intents=discord.Intents.all())

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.StreamHandler()])

COMMAND_LATENCY = Histogram(
    "discord_command_latency_seconds",
    "Latency of Discord bot commands in seconds",
    ["command_name"]
)

@bot.event
async def on_ready():
    logging.info(f"{bot.user} is ready and online!")

@bot.event
async def on_command(ctx):
    command_name = ctx.command.name
    start_time = time.time()
    await bot.invoke(ctx)
    latency = time.time() - start_time
    COMMAND_LATENCY.labels(command_name=command_name).observe(latency)


if __name__ == '__main__':
    if os.path.isdir("commands"):
        os.chdir("commands")
    else:
        os.chdir("app/commands")
    for i in os.listdir():
        if i.endswith(".py"):
            try:
                bot.load_extension(f"commands.{i[:-3]}")
            except Exception as error:
                logging.error(f'{i} could not be loaded. [{error}]')
            else:
                logging.error(f"{i} was loaded correctly")
    if os.path.isdir("./../events"):
        os.chdir("./../events")
    else:
        os.chdir("./../app/events")
    for i in os.listdir():
        if i.endswith(".py"):
            try:
                bot.load_extension(f"events.{i[:-3]}")
            except Exception as error:
                logging.error(f'{i} could not be loaded [{error}]')
            else:
                logging.error(f"{i} was loaded correctly")

    if os.path.isdir("./../temp-voice"): # if the temp-voice folder exists
        os.chdir("./../temp-voice") # change the directory to the temp-voice folder
    else:
        os.chdir("./../temp-voice") # change the directory to the app/temp-voice folder
    for i in os.listdir(): # for every file in the directory
        if i.endswith(".py"): # if the file is a python file
            try:
                bot.load_extension(f"temp-voice.{i[:-3]}") # load the extension
            except Exception as error: # if there is an error
                logging.error(f'{i} could not be loaded. [{error}]') # print the error
            else:
                logging.error(f"{i} was loaded correctly") # print that the file was loaded


bot.run(os.getenv('TOKEN')) # run the bot with the token