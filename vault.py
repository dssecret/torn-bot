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
import asyncio


class Vault(commands.Cog):
    def __init__(self, bot, config, log_file, server):
        self.bot = bot
        self.config = config
        self.log_file = log_file
        self.server = server

    @commands.command(aliases=["req", "with"])
    @commands.cooldown(1, 30 ,commands.BucketType.user)
    async def withdraw(self, ctx, arg):
        '''
        Sends a message to faction leadership (assuming you have enough funds in the vault and you are a member of the
        specific faction)
        '''

        def check(reaction, user):
            return not user.bot

        sender = None
        if ctx.message.author.nick is None:
            sender = ctx.message.author.name
        else:
            sender = ctx.message.author.nick

        senderid = get_torn_id(sender)
        sender = remove_torn_id(sender)

        value = text_to_num(arg)
        log(sender + " has submitted a request for " + arg + ".", self.log_file)

        primary_faction = requests.get(f'https://api.torn.com/faction/?selections=&key='
                                       f'{self.config["DEFAULT"]["TornAPIKey"]}')
        secondary_faction = requests.get(f'https://api.torn.com/faction/?selections=&key='
                                       f'{self.config["DEFAULT"]["TornAPIKey2"]}')

        await ctx.message.delete()

        if primary_faction.status_code != 200:
            embed = discord.Embed()
            embed.title = "Error"
            embed.description = f'Something has possibly gone wrong with the request to the Torn API with HTTP status' \
                                f' code {primary_faction.status_code} has been given at {datetime.datetime.now()}.'
            await ctx.send(embed=embed)

            log(f'The Torn API has responded with HTTP status code {primary_faction.status_code}.', self.log_file)
            return None

        if senderid in primary_faction.json()["members"]:
            request = requests.get(f'https://api.torn.com/faction?selections=donations&key='
                                   f'{self.config["DEFAULT"]["TornAPIKey"]}')

            if request.status_code != 200:
                embed = discord.Embed()
                embed.title = "Error"
                embed.description = f'Something has possibly gone wrong with the request to the Torn API with ' \
                                    f'HTTP status code {request.status_code} has been given at ' \
                                    f'{datetime.datetime.now()}.'
                await ctx.send(embed=embed)

                log(f'The Torn API (2nd Key) has responded with HTTP status code {request.status_code}.', self.log_file)
                return None

            request = request.json()["donations"]

            if int(value) > request[senderid]["money_balance"]:
                log(f'{sender} has requested {arg}, but only has {request[senderid]["money_balance"]} in '
                    f'the vault.', self.log_file)
                await ctx.send(f'You do not have {arg} in the faction vault.')
                return None
            else:
                channel = discord.utils.get(self.server.channels, name=self.config["VAULT"]["Channel"])

                log(f'{sender} has successfully requested {arg} from the faction vault.', self.log_file)

                embed = discord.Embed()
                embed.title = "Money Request"
                embed.description = "Your request has been forwarded to the faction leadership."
                message = await ctx.send(embed=embed)

                embed = discord.Embed()
                embed.title = "Money Request"
                embed.description = f'{sender} is requesting {arg} from the faction vault.'
                embed.set_footer(text=str(message.id))
                message = await channel.send(self.config["VAULT"]["Role"], embed=embed)
                await message.add_reaction('✅')

                reaction = None
                user = None

                while True:
                    if str(reaction) == '✅':
                        log(f'{user.name} has fulfilled the request ({reaction.message.embeds[0].description}).',
                            self.log_file)

                        original = await ctx.fetch_message(int(message.embeds[0].footer.text))

                        embed = discord.Embed()
                        embed.description = f'The request has been fulfilled by {user.name} at {time.ctime()}.'
                        embed.add_field(name="Original Message", value=original.embeds[0].description)
                        await original.edit(embed=embed)

                        embed = discord.Embed()
                        embed.title = "Money Request"
                        embed.description = f'The request has been fulfilled by {user.name} at {time.ctime()}.'
                        embed.add_field(name="Original Message", value=reaction.message.embeds[0].description)

                        await reaction.message.edit(embed=embed)
                        await reaction.message.clear_reactions()
                        await asyncio.sleep(30)
                        await original.delete()
                        return None
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=3600, check=check)
                        await message.clear_reactions()
                    except:
                        break
                return None
        elif senderid in secondary_faction.json()["members"]:
            request = requests.get(f'https://api.torn.com/faction?selections=donations&key='
                                   f'{self.config["DEFAULT"]["TornAPIKey2"]}')

            if request.status_code != 200:
                embed = discord.Embed()
                embed.title = "Error"
                embed.description = f'Something has possibly gone wrong with the request to the Torn API with ' \
                                    f'HTTP status code {request.status_code} has been given at ' \
                                    f'{datetime.datetime.now()}.'
                await ctx.send(embed=embed)

                log(f'The Torn API (2nd Key) has responded with HTTP status code {request.status_code}.', self.log_file)
                return None

            request = request.json()["donations"]

            if int(value) > request[senderid]["money_balance"]:
                log(f'{sender} has requested {arg}, but only has {request[senderid]["money_balance"]} in '
                    f'the vault.', self.log_file)
                await ctx.send(f'You do not have {arg} in the faction vault.')
                return None
            else:
                channel = discord.utils.get(self.server.channels, name=self.config["VAULT"]["Channel2"])

                log(f'{sender} has successfully requested {arg} from the faction vault.', self.log_file)

                embed = discord.Embed()
                embed.title = "Money Request"
                embed.description = "Your request has been forwarded to the faction leadership."
                message = await ctx.send(embed=embed)

                embed = discord.Embed()
                embed.title = "Money Request"
                embed.description = f'{sender} is requesting {arg} from the faction vault.'
                embed.set_footer(text=str(message.id))
                message = await channel.send(self.config["VAULT"]["Role2"], embed=embed)
                await message.add_reaction('✅')

                reaction = None
                user = None

                while True:
                    if str(reaction) == '✅':
                        log(f'{user.name} has fulfilled the request ({reaction.message.embeds[0].description}).',
                            self.log_file)

                        original = await ctx.fetch_message(int(message.embeds[0].footer.text))

                        embed = discord.Embed()
                        embed.description = f'The request has been fulfilled by {user.name} at {time.ctime()}.'
                        embed.add_field(name="Original Message", value=original.embeds[0].description)
                        await original.edit(embed=embed)

                        embed = discord.Embed()
                        embed.title = "Money Request"
                        embed.description = f'The request has been fulfilled by {user.name} at {time.ctime()}.'
                        embed.add_field(name="Original Message", value=reaction.message.embeds[0].description)

                        await reaction.message.edit(embed=embed)
                        await reaction.message.clear_reactions()
                        await asyncio.sleep(30)
                        await original.delete()
                        return None
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=3600, check=check)
                        await message.clear_reactions()
                    except:
                        break
        else:
            log(f'{sender} who is not a member of stored factions has requested {arg}.', self.log_file)

            embed = discord.Embed()
            embed.title = "Money Request"
            embed.description = f'{sender} is not a member of stored factions has requested {arg}.'
            await ctx.send(embed=embed)
            return None

    @commands.command(pass_context=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def b(self, ctx):
        '''
        Returns a simplified version of the balance of your funds in the vault (assuming you are a member of the
        specific faction)
        '''

        await ctx.message.delete()

        sender = None
        message = None
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
            embed.description = f'Something has possibly gone wrong with the request to the Torn API with HTTP status' \
                                f' {response_status} has been given at {datetime.datetime.now()}.'
            message = await ctx.send(embed=embed)
            await asyncio.sleep(30)
            await message.delete()
            return None

        primary_balance = 0
        secondary_balance = 0
        member = False

        json_response = response.json()['donations']

        for user in json_response:
            if json_response[user]["name"] == sender:
                log(f'{sender} has {num_to_text(json_response[user]["money_balance"])} in the faction vault.',
                    self.log_file)

                primary_balance = json_response[user]["money_balance"]
                member = True
                break

        if self.config["DEFAULT"]["TornAPIKey2"] == "":
            embed = discord.Embed()
            embed.title = f'Vault Balance for {sender}'
            embed.description = f'Faction vault balance: {num_to_text(primary_balance)}'
            message = await ctx.send(embed=embed)
            await asyncio.sleep(30)
            await message.delete()
            return None

        response = requests.get(f'https://api.torn.com/faction/?selections=donations&key='
                                f'{self.config["DEFAULT"]["TornAPIKey2"]}')
        response_status = response.status_code

        if response_status != 200:
            log(f'The Torn API has responded with HTTP status code {response_status}.', self.log_file)

            embed = discord.Embed()
            embed.title = f'Vault Balance for {sender}'
            embed.description = f'Primary faction vault balance: {num_to_text(primary_balance)}\nSecondary ' \
                                f'faction vault balance: Failed'
            message = await ctx.send(embed=embed)
            await asyncio.sleep(30)
            await message.delete()
            return None

        json_response = response.json()['donations']

        for user in json_response:
            if json_response[user]["name"] == sender:
                log(f'{sender} has {num_to_text(json_response[user]["money_balance"])} in the faction vault.',
                    self.log_file)
                secondary_balance = json_response[user]["money_balance"]
                member = True

        if member is not True:
            log(f'{sender} who is not a member of any of the stored factions has requested their vault balance.',
                self.log_file)

            embed = discord.Embed()
            embed.title = "Vault Balance for " + sender
            embed.description = f'{sender} is not a member of any of the stored factions.'
            message = await ctx.send(embed=embed)
            await asyncio.sleep(30)
            await message.delete()
            
        else:
            embed = discord.Embed()
            embed.title = f'Vault Balance for {sender}'
            embed.description = f'Primary faction vault balance: {num_to_text(primary_balance)}\nSecondary ' \
                                f'faction vault balance: {num_to_text(secondary_balance)}'
            message = await ctx.send(embed=embed)
            await asyncio.sleep(30)
            await message.delete()

    @commands.command(aliases=["balance"], pass_context=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def bal(self, ctx):
        '''
        Returns the exact balance of your funds in the vault (assuming you are a member of the specific faction)
        '''

        await ctx.message.delete()

        sender = None
        message = None
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
            embed.description = f'Something has possibly gone wrong with the request to the Torn API with HTTP status' \
                                f' {response_status} has been given at {datetime.datetime.now()}.'
            message = await ctx.send(embed=embed)
            await asyncio.sleep(30)
            await message.delete()
            return None

        primary_balance = 0
        secondary_balance = 0
        member = False

        json_response = response.json()['donations']

        for user in json_response:
            if json_response[user]["name"] == sender:
                log(f'{sender} has {num_to_text(json_response[user]["money_balance"])} in the faction vault.',
                    self.log_file)

                primary_balance = json_response[user]["money_balance"]
                member = True
                break

        if self.config["DEFAULT"]["TornAPIKey2"] == "":
            embed = discord.Embed()
            embed.title = f'Vault Balance for {sender}'
            embed.description = f'Faction vault balance: {commas(primary_balance)}'
            message = await ctx.send(embed=embed)
            await asyncio.sleep(30)
            await message.delete()
            return None

        response = requests.get(f'https://api.torn.com/faction/?selections=donations&key='
                                f'{self.config["DEFAULT"]["TornAPIKey2"]}')
        response_status = response.status_code

        if response_status != 200:
            log(f'The Torn API has responded with HTTP status code {response_status}.', self.log_file)

            embed = discord.Embed()
            embed.title = f'Vault Balance for {sender}'
            embed.description = f'Primary faction vault balance: {commas(primary_balance)}\nSecondary ' \
                                f'faction vault balance: Failed'
            message = await ctx.send(embed=embed)
            await asyncio.sleep(30)
            await message.delete()
            return None

        json_response = response.json()['donations']

        for user in json_response:
            if json_response[user]["name"] == sender:
                log(f'{sender} has {num_to_text(json_response[user]["money_balance"])} in the faction vault.',
                    self.log_file)
                secondary_balance = json_response[user]["money_balance"]
                member = True

        if member is not True:
            log(f'{sender} who is not a member of any of the stored factions has requested their vault balance.',
                self.log_file)

            embed = discord.Embed()
            embed.title = "Vault Balance for " + sender
            embed.description = f'{sender} is not a member of any of the stored factions.'
            message = await ctx.send(embed=embed)
            await asyncio.sleep(30)
            await message.delete()
        else:
            embed = discord.Embed()
            embed.title = f'Vault Balance for {sender}'
            embed.description = f'Primary faction vault balance: {commas(primary_balance)}\nSecondary ' \
                                f'faction vault balance: {commas(secondary_balance)}'
            message = await ctx.send(embed=embed)
            await asyncio.sleep(30)
            await message.delete()
