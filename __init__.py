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
    config_file = open('config.ini')
    config_file.close()
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


def num_to_text(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


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

    embed = discord.Embed()
    embed.title = "Latency"
    embed.description = str(latency) + " seconds"
    await ctx.send(embed=embed)


@bot.command()
async def withdraw(ctx, arg):
    '''
    Sends a message to faction leadership (assuming you have enough funds in the vault and you are a member of the specific faction)
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
        embed = discord.Embed()
        embed.title("Error")
        embed.description("Something has possibly gone wrong with the request to the Torn API. HTTP status code " +
                          str(response_status) + " has been given at " + str(datetime.datetime.now()))
        await ctx.send(embed=embed)
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

                    embed = discord.Embed()
                    embed.title = "Money Request"
                    embed.description = "Your request has been forwarded to the faction leadership."
                    await ctx.send(embed=embed)

                    embed = discord.Embed()
                    embed.title = "Money Request"
                    if config["VAULT"]["Role"] == "":
                        embed.description = sender + " is requesting " + arg + " from the faction vault."
                    else:
                        embed.description = config["VAULT"]["Role"] + " " + sender + " is requesting " + arg + " from the faction vault."
                    await channel.send(embed=embed)
                    return None
    else:
        faction = requests.get('https://api.torn.com/faction/?selections=basic&key=' + str(config["DEFAULT"]["TornAPIKey"]))
        file.write(str(datetime.datetime.now()) + " -- " + sender + " who is not a member of " + faction.json()["name"] + " has requested " + arg + ".\n")

        embed = discord.Embed()
        embed.title = "Money Request"
        embed.description = sender + " is not a member of " + faction.json()["name"] + "."
        await ctx.send(embed=embed)


@bot.command()
async def balance(ctx):
    '''
    Returns the balance of your funds in the vault (assuming you are a member of the specific faction)
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
        embed = discord.Embed()
        embed.title("Error")
        embed.description("Something has possibly gone wrong with the request to the Torn API. HTTP status code " +
                          str(response_status) + " has been given at " + str(datetime.datetime.now()))
        await ctx.send(embed=embed)
        return None

    json_response = response.json()['donations']

    for user in json_response:
        if json_response[user]["name"] == sender:
            file.write(str(datetime.datetime.now()) + " -- " + sender + " has " + num_to_text(json_response[user]["money_balance"]) + " in the vault.\n")

            embed = discord.Embed()
            embed.title = "Vault Balance for " + sender
            embed.description = "You have " + num_to_text(json_response[user]["money_balance"]) + " in the faction vault."
            await ctx.send(embed=embed)
            return None
    else:
        faction = requests.get('https://api.torn.com/faction/?selections=basic&key=' + str(config["DEFAULT"]["TornAPIKey"]))
        file.write(str(datetime.datetime.now()) + " -- " + sender + " who is not a member of " + faction.json()["name"] + " has requested their balance.\n")

        embed = discord.Embed()
        embed.title = "Vault Balance for " + sender
        embed.description = sender + " is not a member of " + faction.json()["name"] + "."
        await ctx.send(embed=embed)


@bot.command()
async def setvaultchannel(ctx):
    '''
    Sets the channel that withdrawal messages are sent to
    '''
    config["VAULT"]["Channel"] = str(ctx.message.channel)
    file.write(str(datetime.datetime.now()) + " -- Vault Channel has been set to " + config["VAULT"]["Channel"] + ".\n")

    embed = discord.Embed()
    embed.title = "Vault Channel"
    embed.description = "Vault Channel has been set to " + config["VAULT"]["Channel"] + "."
    await ctx.send(embed=embed)

    with open('config.ini', 'w') as config_file:
        config.write(config_file)


@bot.command()
async def setvaultrole(ctx, role: discord.Role):
    '''
    Sets the role is pinged with withdrawal messages
    '''
    config["VAULT"]["Role"] = str(role.mention)
    file.write(str(datetime.datetime.now()) + " -- Vault Role has been set to " + config["VAULT"]["Role"] + ".\n")

    embed = discord.Embed()
    embed.title = "Vault Role"
    embed.description = "Vault Role has been set to " + config["VAULT"]["Role"] + "."
    await ctx.send(embed=embed)

    with open('config.ini', 'w') as config_file:
        config.write(config_file)


if __name__ == "__main__":
    bot.run(config["DEFAULT"]["BotToken"])
