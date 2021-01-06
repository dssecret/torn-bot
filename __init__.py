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
import time

config = ConfigParser()

try:
    config_file = open('config.ini')
    config_file.close()
except FileNotFoundError:
    with open('config.ini', 'w') as config_file:
        bottoken = input("Please input the bot token: ")

        config["DEFAULT"] = {
            "tornapikey": "",
            "bottoken": bottoken,
            "prefix": ""
        }
        config["VAULT"] = {
            "channel": "",
            "role": ""
        }
        config.write(config_file)

config.read("config.ini")

prefix = "?"
if config["DEFAULT"]["Prefix"] != "":
    prefix = config["DEFAULT"]["Prefix"]

bot = commands.Bot(command_prefix=prefix, help_command=None)
client = discord.client.Client()
intents = discord.Intents.default()
intents.reactions = True

file = open("log.txt", "a")

decimal = {
    'K': 3,
    "M": 6,
    "B": 9
}


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


def check_admin(member):
    return True if member.guild_permissions.administrator else False


def remove_torn_id(name):
    return re.sub("[\(\[].*?[\)\]]", "", name)[:-1]


def log(message):
    file.write(str(datetime.datetime.now()) + " -- " + message + "\n")
    file.flush()


@bot.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == "✅" and not user.bot:
        log(user.name + " has fulfilled the request (" + reaction.message.embeds[0].description + ").")

        embed = discord.Embed()
        embed.title = "Money Request"
        embed.description = "The request has been fulfilled by " + user.name + " at " + time.ctime() + "."
        embed.add_field(name="Original Message", value=reaction.message.embeds[0].description)

        await reaction.message.edit(embed=embed)
        await reaction.message.clear_reactions()


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
    log("Latency: " + str(latency) + ".")

    embed = discord.Embed()
    embed.title = "Latency"
    embed.description = str(latency) + " seconds"
    await ctx.send(embed=embed)


@bot.command(aliases=["req", "with"])
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

    log(sender + " has submitted a request for " + arg + ".")

    response = requests.get('https://api.torn.com/faction/?selections=donations&key=' + str(config["DEFAULT"]["TornAPIKey"]))
    response_status = response.status_code

    log("The Torn API has responded with HTTP status code " + str(response_status) + ".")

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
                log(sender + " has requested " + str(arg) + ", but only has " + str(json_response[user]["money_balance"]) + " in the vault.")
                await ctx.send("You do not have " + arg + " in the faction vault.")
                return None
            else:
                channel = None
                for guild in bot.guilds:
                    channel = discord.utils.get(guild.channels, name=config["VAULT"]["Channel"])

                    log(sender + " has successfully requested " + arg + " from the vault.")

                    embed = discord.Embed()
                    embed.title = "Money Request"
                    embed.description = "Your request has been forwarded to the faction leadership."
                    await ctx.send(embed=embed)

                    embed = discord.Embed()
                    embed.title = "Money Request"
                    embed.description = sender + " is requesting " + arg + " from the faction vault."
                    message = await channel.send(config["VAULT"]["Role"], embed=embed)
                    await message.add_reaction('✅')

                    return None
    else:
        faction = requests.get('https://api.torn.com/faction/?selections=basic&key=' + str(config["DEFAULT"]["TornAPIKey"]))
        log(sender + " who is not a member of " + faction.json()["name"] + " has requested " + arg + ".")

        embed = discord.Embed()
        embed.title = "Money Request"
        embed.description = sender + " is not a member of " + faction.json()["name"] + "."
        await ctx.send(embed=embed)


@bot.command(aliases=["bal"])
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

    log(sender + " is checking their balance in the faction vault.")

    response = requests.get('https://api.torn.com/faction/?selections=donations&key=' + str(config["DEFAULT"]["TornAPIKey"]))
    response_status = response.status_code

    log("The Torn API has responded with HTTP status code " + str(response_status) + ".")

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
            log(sender + " has " + num_to_text(json_response[user]["money_balance"]) + " in the vault.")

            embed = discord.Embed()
            embed.title = "Vault Balance for " + sender
            embed.description = "You have " + num_to_text(json_response[user]["money_balance"]) + " in the faction vault."
            await ctx.send(embed=embed)
            return None
    else:
        faction = requests.get('https://api.torn.com/faction/?selections=basic&key=' + str(config["DEFAULT"]["TornAPIKey"]))
        log(sender + " who is not a member of " + faction.json()["name"] + " has requested their balance.")

        embed = discord.Embed()
        embed.title = "Vault Balance for " + sender
        embed.description = sender + " is not a member of " + faction.json()["name"] + "."
        await ctx.send(embed=embed)


@bot.command(aliases=["svc"])
async def setvaultchannel(ctx):
    '''
    Sets the channel that withdrawal messages are sent to
    '''

    if not check_admin(ctx.message.author):
        embed = discord.Embed()
        embed.title = "Permission Denied"
        embed.description = "This command requires the sender to be an Administrator. This interaction has been logged."
        await ctx.send(embed=embed)

        log(ctx.message.author + " has attempted to run setvaultchannel, but is not an Administrator.")
        return None

    config["VAULT"]["Channel"] = str(ctx.message.channel)
    log("Vault Channel has been set to " + config["VAULT"]["Channel"] + ".")

    embed = discord.Embed()
    embed.title = "Vault Channel"
    embed.description = "Vault Channel has been set to " + config["VAULT"]["Channel"] + "."
    await ctx.send(embed=embed)

    with open('config.ini', 'w') as config_file:
        config.write(config_file)


@bot.command(aliases=["svr"])
async def setvaultrole(ctx, role: discord.Role):
    '''
    Sets the role is pinged with withdrawal messages
    '''

    if not check_admin(ctx.message.author):
        embed = discord.Embed()
        embed.title = "Permission Denied"
        embed.description = "This command requires the sender to be an Administrator. This interaction has been logged."
        await ctx.send(embed=embed)

        log(ctx.message.author + " has attempted to run setvaultrole, but is not an Administrator.")
        return None

    config["VAULT"]["Role"] = str(role.mention)
    log("Vault Role has been set to " + config["VAULT"]["Role"] + ".")

    embed = discord.Embed()
    embed.title = "Vault Role"
    embed.description = "Vault Role has been set to " + config["VAULT"]["Role"] + "."
    await ctx.send(embed=embed)

    with open('config.ini', 'w') as config_file:
        config.write(config_file)


@bot.command(aliases=["sp"])
async def setprefix(ctx, arg="?"):
    '''
    Sets the prefix for the bot
    '''

    if not check_admin(ctx.message.author):
        embed = discord.Embed()
        embed.title = "Permission Denied"
        embed.description = "This command requires the sender to be an Administrator. This interaction has been logged."
        await ctx.send(embed=embed)

        log(ctx.message.author + " has attempted to run setprefix, but is not an Administrator.")
        return None

    config["DEFAULT"]["Prefix"] = str(arg)
    log("Bot prefix has been set to " + config["DEFAULT"]["Prefix"] + ".")

    embed = discord.Embed()
    embed.title = "Bot Prefix"
    embed.description = "Bot prefix has been set to " + config["DEFAULT"]["Prefix"] + ". The bot requires a restart for the prefix change to go into effect."
    await ctx.send(embed=embed)

    with open('config.ini', 'w') as config_file:
        config.write(config_file)


@bot.command()
async def prefix(ctx):
    '''
    Returns the prefix for the bot
    '''

    embed = discord.Embed()
    embed.title = "Bot Prefix"
    embed.description = "The bot prefix is " + config["DEFAULT"]["Prefix"] + "."
    await ctx.send(embed=embed)


@bot.command()
async def help(ctx, arg=None):
    embed = discord.Embed()
    command_list = [command.name for command in bot.commands]

    if not arg:
        embed.description = "Server: " + ctx.guild.name + "\nPrefix: " + ctx.prefix
        embed.add_field(name="GitHub Repository", value="https://github.com/dssecret/torn-bot")
        embed.add_field(name="GitHub Issues", value="https://github.com/dssecret/torn-bot/issues")
        embed.add_field(name="Documentation (Under Construction)", value="https://github.com/dssecret/torn-bot/wiki")
        embed.add_field(name="Torn City User", value="https://www.torn.com/profiles.php?XID=2383326")
        embed.add_field(name="Discord User", value="dssecret#8137")
        embed.add_field(name="For More Information", value="Please contact me (preferably on Discord or Github).")
    elif arg in command_list:
        embed.add_field(name=arg, value=bot.get_command(arg).help)
    else:
        embed.description = "This command does not exist."

    await ctx.send(embed=embed)


if __name__ == "__main__":
    bot.run(config["DEFAULT"]["BotToken"])
    file.close()
