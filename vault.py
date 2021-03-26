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

import discord
from discord.ext import commands

from required import *
import dbutils

import time
import asyncio


class Vault(commands.Cog):
    def __init__(self, bot, log_file, access):
        self.bot = bot
        self.log_file = log_file
        self.access_file = access

    @commands.command(aliases=["req", "with"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def withdraw(self, ctx, arg):
        '''
        Sends a message to faction leadership (assuming you have enough funds in the vault and you are a member of the
        specific faction)
        '''

        # sender = None
        if ctx.message.author.nick is None:
            sender = ctx.message.author.name
        else:
            sender = ctx.message.author.nick

        senderid = get_torn_id(sender)
        sender = remove_torn_id(sender)

        if dbutils.get_user(ctx.message.author.id, "tornid") == "":
            verification = await tornget(ctx, f'https://api.torn.com/user/{senderid}?selections=discord&key=')

            if verification["discord"]["discordID"] != str(ctx.message.author.id) and \
                    verification["discord"]["discordID"] != "":
                embed = discord.Embed()
                embed.title = "Permission Denied"
                embed.description = f'The nickname of {ctx.message.author.nick} in {ctx.guild.name} does not reflect ' \
                                    f'the Torn ID and username. Please update the nickname (i.e. through YATA) or add' \
                                    f' your ID to the database via the `?addid` or `addkey` commands (NOTE: the ' \
                                    f'`?addkey` command requires your Torn API key). This interaction has been logged.'
                await ctx.send(embed=embed)
                log(f'{ctx.message.author.id} (known as {ctx.message.author.name} does not have an accurate nickname, '
                    f'and attempted to withdraw some money from the faction vault.', self.access_file)
                return None

        value = text_to_num(arg)
        log(sender + " has submitted a request for " + arg + ".", self.log_file)

        primary_faction = await tornget(ctx, "https://api.torn.com/faction/?selections=&key=")

        secondary_faction = None
        if dbutils.get_guild(ctx.guild.id, "tornapikey2") != "":
            secondary_faction = await tornget(ctx, "https://api.torn.com/faction/?selections=&key=", guildkey=2)

        await ctx.message.delete()

        if senderid in primary_faction["members"]:
            request = await tornget(ctx, "https://api.torn.com/faction/?selections=donations&key=")
            request = request["donations"]

            if int(value) > request[senderid]["money_balance"]:
                log(f'{sender} has requested {arg}, but only has {request[senderid]["money_balance"]} in '
                    f'the vault.', self.log_file)
                await ctx.send(f'You do not have {arg} in the faction vault.')
                return None
            else:
                channel = discord.utils.get(ctx.guild.channels, name=dbutils.get_vault(ctx.guild.id, "channel"))

                log(f'{sender} has successfully requested {arg} from the faction vault.', self.log_file)

                requestid = dbutils.read("requests")["nextrequest"]

                embed = discord.Embed()
                embed.title = f'Money Request #{dbutils.read("requests")["nextrequest"]}'
                embed.description = "Your request has been forwarded to the faction leadership."
                original = await ctx.send(embed=embed)

                embed = discord.Embed()
                embed.title = f'Money Request #{dbutils.read("requests")["nextrequest"]}'
                embed.description = f'{sender} is requesting {arg} from the faction vault. To fulfill this request, ' \
                                    f'enter `?f {requestid}` in this channel.'
                message = await channel.send(dbutils.get_vault(ctx.guild.id, "role"), embed=embed)

                data = dbutils.read("requests")
                data["nextrequest"] += 1
                data[requestid] = {
                    "requester": ctx.message.author.id,
                    "timerequested": time.ctime(),
                    "fulfiller": None,
                    "timefulfilled": "",
                    "requestmessage": original.id,
                    "withdrawmessage": message.id,
                    "fulfilled": False,
                    "faction": 1
                }
                dbutils.write("requests", data)

        elif senderid in secondary_faction["members"]:
            request = await tornget(ctx, "https://api.torn.com/faction?selections=donations&key=", guildkey=2)
            request = request["donations"]

            if int(value) > request[senderid]["money_balance"]:
                log(f'{sender} has requested {arg}, but only has {request[senderid]["money_balance"]} in '
                    f'the vault.', self.log_file)
                await ctx.send(f'You do not have {arg} in the faction vault.')
                return None
            else:
                channel = discord.utils.get(ctx.guild.channels, name=dbutils.get_vault(ctx.guild.id, "channel2"))

                log(f'{sender} has successfully requested {arg} from the faction vault.', self.log_file)

                requestid = dbutils.read("requests")["nextrequest"]

                embed = discord.Embed()
                embed.title = f'Money Request #{dbutils.read("requests")["nextrequest"]}'
                embed.description = "Your request has been forwarded to the faction leadership."
                original = await ctx.send(embed=embed)

                embed = discord.Embed()
                embed.title = f'Money Request #{dbutils.read("requests")["nextrequest"]}'
                embed.description = f'{sender} is requesting {arg} from the faction vault. To fulfill this request, ' \
                                    f'enter `?f {requestid}` in this channel.'
                message = await channel.send(dbutils.get_vault(ctx.guild.id, "role"), embed=embed)

                data = dbutils.read("requests")
                data["nextrequest"] += 1
                data[requestid] = {
                    "requester": ctx.message.author.id,
                    "timerequested": time.ctime(),
                    "fulfiller": None,
                    "timefulfilled": "",
                    "requestmessage": original.id,
                    "withdrawmessage": message.id,
                    "fulfilled": False,
                    "faction": 2
                }
                dbutils.write("requests", data)
        else:
            log(f'{sender} who is not a member of stored factions has requested {arg}.', self.log_file)

            embed = discord.Embed()
            embed.title = "Money Request"
            embed.description = f'{sender} is not a member of stored factions has requested {arg}.'
            await ctx.send(embed=embed)
            return None

    @commands.command(aliases=['f'])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def fulfill(self, ctx, request):
        '''
        Indicates the fulfillment of the specified request
        '''

        if dbutils.read("requests")[request]["fulfilled"]:
            embed = discord.Embed()
            embed.title = "Request Already Fulfilled"
            embed.description = f'Request #{request} has already been fulfilled by ' \
                                f'{ctx.guild.get_member(dbutils.read("requests")[request]["fulfiller"]).name} ' \
                                f'at {dbutils.read("requests")[request]["timefulfilled"]}.'
            await ctx.send(embed=embed)
            return None

        await ctx.message.delete()

        if dbutils.read("requests")[request]["faction"] == 1:
            channel = discord.utils.get(ctx.guild.channels, id=int(dbutils.get_vault(ctx.guild.id, "banking")))
        else:
            channel = discord.utils.get(ctx.guild.channels, id=int(dbutils.get_vault(ctx.guild.id, "banking2")))
        original = await channel.fetch_message(int(dbutils.read("requests")[request]["requestmessage"]))

        embed = discord.Embed()
        embed.title = original.embeds[0].title

        channel = discord.utils.get(ctx.guild.channels, name=dbutils.get_vault(ctx.guild.id, "channel"))
        message = await channel.fetch_message(int(dbutils.read("requests")[request]["withdrawmessage"]))

        embed.add_field(name='Original Message', value=message.embeds[0].description)
        embed.description = f'The request has been fulfilled by {ctx.message.author.name} at {time.ctime()}.'
        await message.edit(embed=embed)

        embed.description = f'The request has been fulfilled by {ctx.message.author.name} at {time.ctime()}.'
        embed.clear_fields()
        await original.edit(embed=embed)

        data = dbutils.read("requests")
        data[request]["fulfiller"] = ctx.message.author.id
        data[request]["fulfilled"] = True
        data[request]["timefulfilled"] = time.ctime(),
        dbutils.write("requests", data)

        await asyncio.sleep(60)
        await original.delete()

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

        senderid = get_torn_id(sender)
        sender = remove_torn_id(sender)

        if dbutils.get_user(ctx.message.author.id, "tornid") == "":
            verification = await tornget(ctx, f'https://api.torn.com/user/{senderid}?selections=discord&key=')
            if verification["discord"]["discordID"] != str(ctx.message.author.id) and \
                    verification["discord"]["discordID"] != "":
                embed = discord.Embed()
                embed.title = "Permission Denied"
                embed.description = f'The nickname of {ctx.message.author.name} in {ctx.guild.name} does not reflect ' \
                                    f'the Torn ID and username. Please update the nickname (i.e. through YATA) or add' \
                                    f' your ID to the database via the `?addid` or `addkey` commands (NOTE: the ' \
                                    f'`?addkey` command requires your Torn API key). This interaction has been logged.'
                await ctx.send(embed=embed)
                log(f'{ctx.message.author.id} does not have an accurate nickname, and attempted to withdraw'
                    f' some money from the faction vault.', self.access_file)
                return None

        log(f'{sender} is checking their balance in the faction vault.', self.log_file)

        response = await tornget(ctx, "https://api.torn.com/faction/?selections=donations&key=")
        response = response["donations"]

        primary_balance = 0
        secondary_balance = 0
        member = False

        for user in response:
            if response[user]["name"] == sender:
                log(f'{sender} has {num_to_text(response[user]["money_balance"])} in the faction vault.',
                    self.log_file)

                primary_balance = response[user]["money_balance"]
                member = True
                break

        if dbutils.get_guild(ctx.guild.id, "tornapikey2") == "":
            embed = discord.Embed()
            embed.title = f'Vault Balance for {sender}'
            embed.description = f'Faction vault balance: {num_to_text(primary_balance)}'
            message = await ctx.send(embed=embed)
            await asyncio.sleep(30)
            await message.delete()
            return None

        response = await tornget(ctx, "https://api.torn.com/faction/?selections=donations&key=", guildkey=2)
        response = response['donations']

        for user in response:
            if response[user]["name"] == sender:
                log(f'{sender} has {num_to_text(response[user]["money_balance"])} in the faction vault.',
                    self.log_file)
                secondary_balance = response[user]["money_balance"]
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

        senderid = get_torn_id(sender)
        sender = remove_torn_id(sender)

        if dbutils.get_user(ctx.message.author.id, "tornid") == "":
            verification = await tornget(ctx, f'https://api.torn.com/user/{senderid}?selections=discord&key=')
            if verification["discord"]["discordID"] != str(ctx.message.author.id) and \
                    verification["discord"]["discordID"] != "":
                embed = discord.Embed()
                embed.title = "Permission Denied"
                embed.description = f'The nickname of {ctx.message.author.name} in {ctx.guild.name} does not reflect ' \
                                    f'the Torn ID and username. Please update the nickname (i.e. through YATA) or add' \
                                    f' your ID to the database via the `?addid` or `addkey` commands (NOTE: the ' \
                                    f'`?addkey` command requires your Torn API key). This interaction has been logged.'
                await ctx.send(embed=embed)
                log(f'{ctx.message.author.id} does not have an accurate nickname, and attempted to withdraw'
                    f' some money from the faction vault.', self.access_file)
                return None

        log(f'{sender} is checking their balance in the faction vault.', self.log_file)

        response = await tornget(ctx, "https://api.torn.com/faction/?selections=donations&key=")
        response = response["donations"]

        primary_balance = 0
        secondary_balance = 0
        member = False

        for user in response:
            if response[user]["name"] == sender:
                log(f'{sender} has {num_to_text(response[user]["money_balance"])} in the faction vault.',
                    self.log_file)

                primary_balance = response[user]["money_balance"]
                member = True
                break

        if dbutils.get_guild(ctx.guild.id, "tornapikey2") == "":
            embed = discord.Embed()
            embed.title = f'Vault Balance for {sender}'
            embed.description = f'Faction vault balance: {commas(primary_balance)}'
            message = await ctx.send(embed=embed)
            await asyncio.sleep(30)
            await message.delete()
            return None

        response = await tornget(ctx, "https://api.torn.com/faction/?selections=donations&key=", guildkey=2)
        response = response['donations']

        for user in response:
            if response[user]["name"] == sender:
                log(f'{sender} has {num_to_text(response[user]["money_balance"])} in the faction vault.',
                    self.log_file)
                secondary_balance = response[user]["money_balance"]
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
