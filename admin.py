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

from discord.ext import commands, tasks
import discord
import requests

from required import *

import time
import os


class Admin(commands.Cog):
    def __init__(self, config, log_file, bot, client, server, access):
        self.config = config
        self.log_file = log_file
        self.bot = bot
        self.client = client
        self.server = server
        self.access = access

        self.noob.start()

    @commands.command(aliases=["svc"])
    async def setvaultchannel(self, ctx):
        '''
        Sets the channel that withdrawal messages are sent to in config.ini
        '''

        if not check_admin(ctx.message.author) and self.config["DEFAULT"]["Superuser"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator.' \
                                f' This interaction has been logged.'

            await ctx.send(embed=embed)
            log(f'{ctx.message.author.name} has attempted to run setvaultchannel, but is not an Administrator.',
                self.access)
            return None

        self.config["VAULT"]["Channel"] = str(ctx.message.channel)
        log(f'Vault Channel has been set to {ctx.message.channel}.', self.log_file)

        embed = discord.Embed()
        embed.title = "Vault Channel"
        embed.description = f'Vault Channel has been set to {ctx.message.channel}.'
        await ctx.send(embed=embed)

        with open(f'{os.getcwd()}/config.ini', 'w') as config_file:
            self.config.write(config_file)

    @commands.command(aliases=["svr"])
    async def setvaultrole(self, ctx, role: discord.Role):
        '''
        Sets the role is pinged with withdrawal messages in config.ini
        '''

        if not check_admin(ctx.message.author) and self.config["DEFAULT"]["Superuser"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator. ' \
                                f'This interaction has been logged.'
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to run setvaultrole, but is not an Administrator',
                self.access)
            return None

        self.config["VAULT"]["Role"] = str(role.mention)
        log(f'Vault Role has been set to {role.mention}.', self.log_file)

        embed = discord.Embed()
        embed.title = "Vault Role"
        embed.description = f'Vault Role has been set to {role.mention}.'
        await ctx.send(embed=embed)

        with open(f'{os.getcwd()}/config.ini', 'w') as config_file:
            self.config.write(config_file)

    @commands.command(aliases=["sp"])
    async def setprefix(self, ctx, arg="?"):
        '''
        Sets the prefix for the bot in config.ini
        '''

        if not check_admin(ctx.message.author) and self.config["DEFAULT"]["Superuser"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator. ' \
                                f'This interaction has been logged.'
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to run setprefix, but is not an Administrator.',
                self.access)
            return None

        self.config["DEFAULT"]["Prefix"] = str(arg)
        log(f'Bot Prefix has been set to {arg}.', self.log_file)

        embed = discord.Embed()
        embed.title = "Bot Prefix"
        embed.description = f'Bot Prefix has been set to {arg}. The bot requires a restart for the prefix change to ' \
                            f'go into effect.'
        await ctx.send(embed=embed)

        with open(f'{os.getcwd()}/config.ini', 'w') as config_file:
            self.config.write(config_file)

    @commands.command(aliases=["snr"])
    async def setnoobrole(self, ctx, role: discord.Role):
        '''
        Sets the role given to users under level 15 in config.ini
        '''

        if not check_admin(ctx.message.author) and self.config["DEFAULT"]["Superuser"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator. ' \
                                f'This interaction has been logged.'
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to run setnoobrole, but is not an Administrator.',
                self.access)
            return None

        self.config["ROLES"]["Noob"] = str(role.id)
        log(f'Noob Role has been set to {role.id}.', self.log_file)

        embed = discord.Embed()
        embed.title = "Noob Role"
        embed.description = f'Noob Role has been set to {role.name}.'
        await ctx.send(embed=embed)

        with open(f'{os.getcwd()}/config.ini', 'w') as config_file:
            self.config.write(config_file)

    @commands.command()
    async def runnoob(self, ctx):
        '''
        Adds the noob role from all users under level 15. Removes the noob role from all users who have the noob role,
        but are above level 15.
        '''

        start = time.time()

        if not check_admin(ctx.message.author) and self.config["DEFAULT"]["Superuser"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator. ' \
                                f'This interaction has been logged.'
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to run runnoob, but is not an Administrator.', self.access)
            return None

        if self.config["ROLES"]["noob"] == "":
            embed = discord.Embed()
            embed.title = "Missing Role Configuration"
            embed.description = "There needs to be a noob role setup for this command to add that role."
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to run runnoob, but there is no noob role set.',
                self.log_file)
            return None

        embed = discord.Embed()
        embed.title = "Noob Function"
        embed.description = "The noob function is currently running."
        message = await ctx.send(embed=embed)

        response = requests.get(f'https://api.torn.com/faction/?selections=&key={self.config["DEFAULT"]["TornAPIKey"]}')
        if response.status_code != 200:
            log(f'The Torn API has responded with HTTP status code {response.status_code}.', self.log_file)

        members = list(response.json()["members"].keys())

        over15 = self.config["VAULT"]["over15"].split(",")

        if "" in over15:
            over15.remove("")

        for memberover15 in over15:
            if memberover15 == "":
                break
            members.remove(memberover15)

        noob = self.server.get_role(int(self.config["ROLES"]["noob"]))

        for member in members:
            request = requests.get(f'https://api.torn.com/user/{member}?selections=basic,discord&key='
                                   f'{self.config["DEFAULT"]["TornAPIKey"]}')
            if request.status_code != 200:
                log(f'The Torn API has responded with HTTP status code {request.status_code}.', self.log_file)

            discordid = request.json()["discord"]["discordID"]
            if discordid == "":
                continue

            discord_member = self.server.get_member(int(discordid))

            if discord_member is None:
                continue

            if request.json()["level"] > 15:
                over15.append(member)

                if noob in discord_member.roles:
                    await discord_member.remove_roles(noob)
                    log(f'The Noob Role has been removed from {discord_member}.', self.log_file)
                continue

            await discord_member.add_roles(noob)
            log(f'The Noob Role has been added to {discord_member}.', self.log_file)

        outover15 = ",".join(over15)
        self.config["VAULT"]["over15"] = outover15

        with open("config.ini", "w") as config_file:
            self.config.write(config_file)

        embed.description = f'The noob function has finished running and ran for {time.time() - start} seconds.'
        await message.edit(embed=embed)
        log(f'The noob function ran for {time.time() - start} seconds.', self.log_file)

    @tasks.loop(hours=24)
    async def noob(self):
        start = time.time()

        if self.config["DEFAULT"]["noob"] != "True":
            log("The automatic noob function has been aborted due to the noob flag not being set or the noob flag"
                "being set to False", self.log_file)
            return None

        if self.config["ROLES"]["noob"] == "":
            log("There is no noob role set, so the noob setting process has been aborted.", self.log_file)
            return None

        response = requests.get(f'https://api.torn.com/faction/?selections=&key={self.config["DEFAULT"]["TornAPIKey"]}')
        log(f'The Torn API has responded with HTTP status code {response.status_code}.', self.log_file)

        members = list(response.json()["members"].keys())

        over15 = self.config["VAULT"]["over15"].split(",")

        if "" in over15:
            over15.remove("")

        for memberover15 in over15:
            if memberover15 == "":
                break
            members.remove(memberover15)

        noob = self.server.get_role(int(self.config["ROLES"]["noob"]))

        for member in members:
            request = requests.get(f'https://api.torn.com/user/{member}?selections=basic,discord&key='
                                   f'{self.config["DEFAULT"]["TornAPIKey"]}')
            if request.status_code != 200:
                log(f'The Torn API has responded with HTTP status code {response.status_code}.', self.log_file)

            discordid = request.json()["discord"]["discordID"]

            if discordid == "":
                continue
            discord_member = self.server.get_member(int(discordid))

            if discord_member is None:
                continue

            if request.json()["level"] > 15:
                over15.append(member)

                if noob in discord_member.roles:
                    await discord_member.remove_roles(noob)
                    log(f'The Noob role has been removed from {discord_member}.', self.log_file)
                continue

            await discord_member.add_roles(noob)
            log(f'The Noob role has been added to {discord_member}.', self.log_file)

        outover15 = ",".join(over15)
        self.config["VAULT"]["over15"] = outover15

        with open("config.ini", "w") as config_file:
            self.config.write(config_file)

        log(f'The noob function ran for {time.time() - start} seconds.', self.log_file)

    @noob.before_loop
    async def before_noob(self):
        print("Waiting for bot to be ready before running automatic noob function...")
        await self.bot.wait_until_ready()

    @commands.command(pass_context=True)
    async def setguild(self, ctx):
        '''
        Sets the guild ID in config.ini
        '''

        if not check_admin(ctx.message.author) and self.config["DEFAULT"]["Superuser"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator. ' \
                                f'This interaction has been logged.'
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to run setguild, but is not an Administrator.', self.access)
            return None

        self.config["DEFAULT"]["serverid"] = str(ctx.guild.id)
        log(f'The server ID has been set to {ctx.guild.id}.', self.log_file)

        embed = discord.Embed()
        embed.title = "Server ID"
        embed.description = f'The server ID has been set to {ctx.guild.id}.'
        await ctx.send(embed=embed)

        with open(f'{os.getcwd()}/config.ini', 'w') as config_file:
            self.config.write(config_file)

    @commands.command()
    async def enablenoob(self, ctx):
        '''
        Enables automatic running of the noob function every day
        '''

        if not check_admin(ctx.message.author) and self.config["DEFAULT"]["Superuser"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator. ' \
                                f'This interaction has been logged.'
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to run enablenoob, but is not an Administrator',
                self.access)
            return None

        self.config["DEFAULT"]["noob"] = "True"
        log("The automatic noob status has been set to True.", self.log_file)

        embed = discord.Embed()
        embed.title = "Automatic Noob Status"
        embed.description = "The automatic noob status has been set to True, and the noob function will run everyday."
        await ctx.send(embed=embed)

        with open(f'{os.getcwd()}/config.ini', 'w') as config_file:
            self.config.write(config_file)

    @commands.command()
    async def disablenoob(self, ctx):
        '''
        Disables automatic running of the noob function every day
        '''

        if not check_admin(ctx.message.author) and self.config["DEFAULT"]["Superuser"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator. ' \
                                f'This interaction has been logged.'
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to run disablenoob, but is not an Administrator',
                self.access)
            return None

        self.config["DEFAULT"]["noob"] = "False"
        log("The automatic noob status has been set to False.", self.log_file)

        embed = discord.Embed()
        embed.title = "Automatic Noob Status"
        embed.description = "The automatic noob status has been set to False, and the noob function will not" \
                            " run everyday."
        await ctx.send(embed=embed)

        with open(f'{os.getcwd()}/config.ini', 'w') as config_file:
            self.config.write(config_file)

    @commands.command()
    async def config(self, ctx):
        '''
        Returns the current configuration of the bot
        '''

        if not check_admin(ctx.message.author) and self.config["DEFAULT"]["Superuser"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator. ' \
                                f'This interaction has been logged.'
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to run config, but is not an Administrator', self.access)
            return None

        embed = discord.Embed()
        embed.title = "Current Configuration"
        embed.description = f'''Torn API Key: Classified
        Bot Token: Classified
        Prefix: {self.config["DEFAULT"]["Prefix"]}
        Server ID: {self.config["DEFAULT"]["serverid"]}
        Superuser: {self.config["DEFAULT"]["Superuser"]}
        Noob Status: {self.config["DEFAULT"]["noob"]}
        Vault Channel: {self.config["VAULT"]["channel"]}
        Vault Role: {self.config["VAULT"]["role"]}
        Users Over Level 15: {self.config["VAULT"]["over15"]}
        Noob Role ID: {self.config["ROLES"]["noob"]}'''

        await ctx.send(embed=embed)
