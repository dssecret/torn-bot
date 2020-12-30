# This file is part of torn-bot.
# 
# torn-bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# torn-bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with torn-bot.  If not, see <https://www.gnu.org/licenses/>.

from discord.ext import commands
import discord
import requests

import datetime
from decimal import Decimal
import re
import json
from configparser import ConfigParser

prefix = "?"
bot = commands.Bot(command_prefix=prefix)

client = discord.client.Client()

file = open("log.txt", "a")

config = ConfigParser()
config.read("config.ini")

decimal = {
    'K': 3,
    "M": 6,
    "B": 9
}

try:
    file = open('config.ini')
    file.close()
except FileNotFoundError:
    with open('config.ini', 'w') as config_file:
        config["DEFAULT"] = {
            "tornapikey": "",
            "bottoken": ""
        }
        config["VAULT"] = {
            "channel": "",
            "role": ""
        }
        config.write(config_file)


def text_to_num(text):
    text = text.upper()
    if text[-1] in decimal:
        num, magnitude = text[:-1], text[-1]
        return Decimal(num) * 10 ** decimal[magnitude]
    else:
        return Decimal(text)


def remove_torn_id(name):
    return re.sub("[\(\[].*?[\)\]]", "", name)[:-1]


@bot.event
async def on_ready():
    guild_count = 0

    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count = guild_count + 1

    print("Bot is in " + str(guild_count) + " guilds.")


@bot.command()
async def ping(ctx):
    '''
    Shows the ping to the server
    '''

    latency = bot.latency
    file.write(str(datetime.datetime.now()) + " -- Latency: " + str(latency) + ".\n")
    await ctx.send(latency)


@bot.command()
async def withdraw(ctx, arg):
    '''
    Sends a message to faction leadership (assuming you have enough funds in the vault and you are a member of the specific faction).
    '''
    sender = None
    if ctx.message.author.nick is None:
        sender = ctx.message.author.name
    else:
        sender = ctx.message.author.nick

    sender = remove_torn_id(sender)

    value = text_to_num(arg)

    file.write(str(datetime.datetime.now()) + " -- " + sender + " has submitted a request for " + arg + ".\n")

    response = requests.get('https://api.torn.com/faction/?selections=donations&key=' + str(config["DEFAULT"]["TornAPIKey"]))
    response_status = response.status_code

    file.write(str(datetime.datetime.now()) + " -- The Torn API has responded with HTTP status code " + str(response_status) + ".\n")

    if response_status != 200:
        await ctx.send("Something has possibly gone wrong. HTTP status code " + str(response_status) +
                       " has been given at " + str(datetime.datetime.now()))
        return None

    json_response = response.json()['donations']

    for user in json_response:
        if json_response[user]["name"] == sender:
            if int(value) > json_response[user]["money_balance"]:
                file.write(str(datetime.datetime.now()) + " -- " + sender + " has requested " + str(arg) + ", but only has " + str(json_response[user]["money_balance"]) + " in the vault.\n")
                await ctx.send("You do not have " + arg + " in the faction vault.")
                return None
            else:
                channel = None
                for guild in bot.guilds:
                    channel = discord.utils.get(guild.channels, name=config["VAULT"]["Channel"])

                    file.write(str(datetime.datetime.now()) + " -- " + sender + " has successfully requested " + arg + " from the vault.\n")
                    await ctx.send("Your request has been forwarded to the faction leadership.")
                    await channel.send(sender + " is requesting " + arg + " from the faction vault.")
                    return None
    else:
        faction = requests.get('https://api.torn.com/faction/?selections=basic&key=' + str(config["DEFAULT"]["TornAPIKey"]))
        file.write(str(datetime.datetime.now()) + " -- " + sender + " who is not a member of " + faction.json()["name"] + " has requested " + arg + ".\n")
        await ctx.send(sender + " is not a member of " + faction.json()["name"] + ".")


@bot.command()
async def balance(ctx):
    '''
    Returns the balance of your funds in the vault (assuming you are a member of the specific faction).
    '''
    sender = None
    if ctx.message.author.nick is None:
        sender = ctx.message.author.name
    else:
        sender = ctx.message.author.nick

    sender = remove_torn_id(sender)

    file.write(str(datetime.datetime.now()) + " -- " + sender + " is checking their balance in the faction vault.\n")

    response = requests.get('https://api.torn.com/faction/?selections=donations&key=' + str(config["DEFAULT"]["TornAPIKey"]))
    response_status = response.status_code

    file.write(str(datetime.datetime.now()) + " -- The Torn API has responded with HTTP status code " + str(response_status) + ".\n")

    if response_status != 200:
        await ctx.send("Something has possibly gone wrong. HTTP status code " + str(response_status) +
                       " has been given at " + str(datetime.datetime.now()))
        return None

    json_response = response.json()['donations']

    for user in json_response:
        if json_response[user]["name"] == sender:
            file.write(str(datetime.datetime.now()) + " -- " + sender + " has " + str(json_response[user]["money_balance"]) + " in the vault.\n")
            await ctx.send("You have " + str(json_response[user]["money_balance"]) + " in the faction vault.")
            return None
    else:
        faction = requests.get('https://api.torn.com/faction/?selections=basic&key=' + str(config["DEFAULT"]["TornAPIKey"]))
        file.write(str(datetime.datetime.now()) + " -- " + sender + " who is not a member of " + faction.json()["name"] + " has requested their balance.\n")
        await ctx.send(sender + " is not a member of " + faction.json()["name"] + ".")


@bot.command()
async def setvaultchannel(ctx):
    '''
    Sets the channel that withdrawl messages are sent to.
    '''
    config["VAULT"]["Channel"] = str(ctx.message.channel)
    await ctx.send("Vault Channel has been set to " + config["VAULT"]["Channel"] + ".")
    file.write(str(datetime.datetime.now()) + " -- Vault Channel has been set to " + config["VAULT"]["Channel"] + ".\n")

    with open('config.ini', 'w') as config_file:
        config.write(config_file)


if __name__ == "__main__":
    bot.run(config["DEFAULT"]["BotToken"])
