# This file is part of torn-bot.
# 
# torn-bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
# 
# torn-bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with torn-bot.  If not, see <https://www.gnu.org/licenses/>.

from discord.ext import commands
import discord

from configparser import ConfigParser

import vault
import admin
from required import *

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

bot.add_cog(vault.Vault(bot, config, file))
bot.add_cog(admin.Admin(config, file))


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
    log("Latency: " + str(latency) + ".", file)

    embed = discord.Embed()
    embed.title = "Latency"
    embed.description = str(latency) + " seconds"
    await ctx.send(embed=embed)


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
    '''
    Returns links to the documentation, issues, developer contact information, and other pages if no command is passed
    as a paramter. If a command is passed as a paramter, the help command returns the help message of the passed
    command.
    '''

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
