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
            log(f'{user.name} has fulfilled the request ({reaction.message.embeds[0].description}).', self.log_file)

            embed = discord.Embed()
            embed.title = "Money Request"
            embed.description = f'The request has been fulfilled by {user.name} at {time.ctime()}.'
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
    
        response = requests.get(f'https://api.torn.com/faction/?selections=donations&key='
                                f'{self.config["DEFAULT"]["TornAPIKey"]}')
        response_status = response.status_code
    
        if response_status != 200:
            embed = discord.Embed()
            embed.title = "Error"
            embed.description = f'Something has possibly gone wrong with the request to the Torn API with HTTP' \
                                f' status code {response_status} has been given at {datetime.datetime.now()}.'
            await ctx.send(embed=embed)

            log(f'The Torn API has responded with HTTP status code {response_status}.', self.log_file)
            return None
    
        json_response = response.json()['donations']
    
        for user in json_response:
            if json_response[user]["name"] == sender:
                if int(value) > json_response[user]["money_balance"]:
                    log(f'{sender} has requested {arg}, but only has {json_response[user]["money_balance"]} in '
                        f'the vault.', self.log_file)
                    await ctx.send(f'You do not have {arg} in the faction vault.')
                    return None
                else:
                    channel = None
                    for guild in self.bot.guilds:
                        channel = discord.utils.get(guild.channels, name=self.config["VAULT"]["Channel"])

                    log(f'{sender} has successfully requested {arg} from the faction vault.', self.log_file)

                    embed = discord.Embed()
                    embed.title = "Money Request"
                    embed.description = "Your request has been forwarded to the faction leadership."
                    await ctx.send(embed=embed)

                    embed = discord.Embed()
                    embed.title = "Money Request"
                    embed.description = f'{sender} is requesting {arg} from the faction vault.'
                    message = await channel.send(self.config["VAULT"]["Role"], embed=embed)
                    await message.add_reaction('✅')

                    return None
        else:
            faction = requests.get(f'https://api.torn.com/faction/?selections=basic&key='
                                   f'{self.config["DEFAULT"]["TornAPIKey"]}')
            log(f'{sender} who is not a member of {faction.json()["name"]} has requested {arg}.', self.log_file)
    
            embed = discord.Embed()
            embed.title = "Money Request"
            embed.description = f'{sender} is not a member of {faction.json()["name"]}.'
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

        log(f'{sender} is checking their balance in the faction vault.', self.log_file)
    
        response = requests.get(f'https://api.torn.com/faction/?selections=donations&key='
                                f'{self.config["DEFAULT"]["TornAPIKey"]}')
        response_status = response.status_code

        if response_status != 200:
            log(f'The Torn API has responded with HTTP status code {response_status}.', self.log_file)

            embed = discord.Embed()
            embed.title = "Error"
            embed.description = f'Something has posibly gone wrong with the request to the Torn API with HTTP status' \
                                f' {response_status} has been given at {datetime.datetime.now()}.'
            await ctx.send(embed=embed)
            return None
    
        json_response = response.json()['donations']
    
        for user in json_response:
            if json_response[user]["name"] == sender:
                log(f'{sender} has {num_to_text(json_response[user]["money_balance"])} in the faction vault.',
                    self.log_file)
    
                embed = discord.Embed()
                embed.title = "Vault Balance for " + sender
                embed.description = f'You have {num_to_text(json_response[user]["money_balance"])} in the ' \
                                    f'faction vault.'
                await ctx.send(embed=embed)
                return None
        else:
            faction = requests.get(f'https://api.torn.com/faction/?selections=basic&key='
                                   f'{self.config["DEFAULT"]["TornAPIKey"]}')
            log(f'{sender} who is not a member of {faction.json()["name"]} has requested their vault balance.',
                self.log_file)
    
            embed = discord.Embed()
            embed.title = "Vault Balance for " + sender
            embed.description = f'{sender} is not a member of {faction.json()["name"]}.'
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

        log(f'{sender} is checking their balance in the faction vault.', self.log_file)
    
        response = requests.get(f'https://api.torn.com/faction/?selections=donations&key='
                                f'{self.config["DEFAULT"]["TornAPIKey"]}')
        response_status = response.status_code

        log(f'The Torn API has responded with HTTP status code {response_status}.', self.log_file)
    
        if response_status != 200:
            embed = discord.Embed()
            embed.title = "Error"
            embed.description = f'Something has possibly gone wrong with the request to the Torn API with HTTP ' \
                                f'status code {response_status} has been given at {datetime.datetime.now()}'
            await ctx.send(embed=embed)
            return None
    
        json_response = response.json()['donations']
    
        for user in json_response:
            if json_response[user]["name"] == sender:
                log(f'{sender} has {json_response[user]["money_balance"]} in the vault', self.log_file)
    
                embed = discord.Embed()
                embed.title = "Vault Balance for " + sender
                embed.description = f'You have {commas(json_response[user]["money_balance"])} in the faction vault.'
                await ctx.send(embed=embed)
                return None
        else:
            faction = requests.get(f'https://api.torn.com/faction/?selections=basic&key='
                                   f'{self.config["DEFAULT"]["TornAPIKey"]}')
            log(f'{sender} who is not a member of {faction.json()["name"]} has requested their balance', self.log_file)
    
            embed = discord.Embed()
            embed.title = f'Vault Balance for {self}'
            embed.description = f'{sender} is not a member of {faction.json()["name"]}.'
            await ctx.send(embed=embed)
