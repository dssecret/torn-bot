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
import requests

from required import *

import time


class Vault(commands.Cog):
    def __init__(self, bot, config, log_file):
        self.bot = bot
        self.config = config
        self.log_file = log_file

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.emoji == "✅" and user.bot is not True:
            log(user.name + " has fulfilled the request (" + reaction.message.embeds[0].description + ").",
                self.log_file)

            embed = discord.Embed()
            embed.title = "Money Request"
            embed.description = "The request has been fulfilled by " + user.name + " at " + time.ctime() + "."
            embed.add_field(name="Original Message", value=reaction.message.embeds[0].description)

            await reaction.message.edit(embed=embed)
            await reaction.message.clear_reactions()

    @commands.command(aliases=["req", "with"])
    async def withdraw(self, ctx, arg):
        '''
        Sends a message to faction leadership (assuming you have enough funds in the vault and you are a member of the
        specific faction)
        '''
    
        sender = None
        if ctx.message.author.nick is None:
            sender = ctx.message.author.name
        else:
            sender = ctx.message.author.nick
    
        sender = remove_torn_id(sender)
    
        value = text_to_num(arg)
    
        log(sender + " has submitted a request for " + arg + ".", self.log_file)
    
        response = requests.get('https://api.torn.com/faction/?selections=donations&key=' +
                                str(self.config["DEFAULT"]["TornAPIKey"]))
        response_status = response.status_code
    
        log("The Torn API has responded with HTTP status code " + str(response_status) + ".", self.log_file)
    
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
                    log(sender + " has requested " + str(arg) + ", but only has " +
                        str(json_response[user]["money_balance"]) + " in the vault.", self.log_file)
                    await ctx.send("You do not have " + arg + " in the faction vault.")
                    return None
                else:
                    channel = None
                    for guild in self.bot.guilds:
                        channel = discord.utils.get(guild.channels, name=self.config["VAULT"]["Channel"])
    
                        log(sender + " has successfully requested " + arg + " from the vault.", self.log_file)
    
                        embed = discord.Embed()
                        embed.title = "Money Request"
                        embed.description = "Your request has been forwarded to the faction leadership."
                        await ctx.send(embed=embed)
    
                        embed = discord.Embed()
                        embed.title = "Money Request"
                        embed.description = sender + " is requesting " + arg + " from the faction vault."
                        message = await channel.send(self.config["VAULT"]["Role"], embed=embed)
                        await message.add_reaction('✅')
    
                        return None
        else:
            faction = requests.get('https://api.torn.com/faction/?selections=basic&key=' +
                                   str(self.config["DEFAULT"]["TornAPIKey"]))
            log(sender + " who is not a member of " + faction.json()["name"] + " has requested " + arg + ".",
                self.log_file)
    
            embed = discord.Embed()
            embed.title = "Money Request"
            embed.description = sender + " is not a member of " + faction.json()["name"] + "."
            await ctx.send(embed=embed)

    @commands.command()
    async def b(self, ctx):
        '''
        Returns a simplified version of the balance of your funds in the vault (assuming you are a member of the
        specific faction)
        '''
        sender = None
        if ctx.message.author.nick is None:
            sender = ctx.message.author.name
        else:
            sender = ctx.message.author.nick
    
        sender = remove_torn_id(sender)
    
        log(sender + " is checking their balance in the faction vault.", self.log_file)
    
        response = requests.get('https://api.torn.com/faction/?selections=donations&key=' +
                                str(self.config["DEFAULT"]["TornAPIKey"]))
        response_status = response.status_code
    
        log("The Torn API has responded with HTTP status code " + str(response_status) + ".", self.log_file)
    
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
                log(sender + " has " + num_to_text(json_response[user]["money_balance"]) + " in the vault.",
                    self.log_file)
    
                embed = discord.Embed()
                embed.title = "Vault Balance for " + sender
                embed.description = "You have " + num_to_text(json_response[user]["money_balance"]) + \
                                    " in the faction vault."
                await ctx.send(embed=embed)
                return None
        else:
            faction = requests.get('https://api.torn.com/faction/?selections=basic&key=' +
                                   str(self.config["DEFAULT"]["TornAPIKey"]))
            log(sender + " who is not a member of " + faction.json()["name"] + " has requested their balance.",
                self.log_file)
    
            embed = discord.Embed()
            embed.title = "Vault Balance for " + sender
            embed.description = sender + " is not a member of " + faction.json()["name"] + "."
            await ctx.send(embed=embed)

    @commands.command(aliases=["balance"])
    async def bal(self, ctx):
        '''
        Returns the exact balance of your funds in the vault (assuming you are a member of the specific faction)
        '''
    
        sender = None
        if ctx.message.author.nick is None:
            sender = ctx.message.author.name
        else:
            sender = ctx.message.author.nick
    
        sender = remove_torn_id(sender)
    
        log(sender + " is checking their balance in the faction vault.", self.log_file)
    
        response = requests.get('https://api.torn.com/faction/?selections=donations&key=' +
                                str(self.config["DEFAULT"]["TornAPIKey"]))
        response_status = response.status_code
    
        log("The Torn API has responded with HTTP status code " + str(response_status) + ".", self.log_file)
    
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
                log(sender + " has " + str(json_response[user]["money_balance"]) + " in the vault.", self.log_file)
    
                embed = discord.Embed()
                embed.title = "Vault Balance for " + sender
                embed.description = "You have " + commas(json_response[user]["money_balance"]) + \
                                    " in the faction vault."
                await ctx.send(embed=embed)
                return None
        else:
            faction = requests.get('https://api.torn.com/faction/?selections=basic&key=' +
                                   str(self.config["DEFAULT"]["TornAPIKey"]))
            log(sender + " who is not a member of " + faction.json()["name"] + " has requested their balance.",
                self.log_file)
    
            embed = discord.Embed()
            embed.title = "Vault Balance for " + sender
            embed.description = sender + " is not a member of " + faction.json()["name"] + "."
            await ctx.send(embed=embed)
