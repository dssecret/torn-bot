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

from required import *


class Admin(commands.Cog):
    def __init__(self, config, log_file, bot, client, server, access):
        self.config = config
        self.log_file = log_file
        self.bot = bot
        self.client = client
        self.server = server
        self.access = access

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

        with open(f'config.ini', 'w') as config_file:
            self.config.write(config_file)

    @commands.command(aliases=["svc2"])
    async def setvaultchannel2(self, ctx):
        '''
        Sets the second channel that withdrawal messages are sent to in config.ini
        '''

        if not check_admin(ctx.message.author) and self.config["DEFAULT"]["Superuser"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator.' \
                                f' This interaction has been logged.'

            await ctx.send(embed=embed)
            log(f'{ctx.message.author.name} has attempted to run setvaultchannel2, but is not an Administrator.',
                self.access)
            return None

        self.config["VAULT"]["Channel2"] = str(ctx.message.channel)
        log(f'Vault Channel 2 has been set to {ctx.message.channel}.', self.log_file)

        embed = discord.Embed()
        embed.title = "Vault Channel"
        embed.description = f'Vault Channel 2 has been set to {ctx.message.channel}.'
        await ctx.send(embed=embed)

        with open(f'config.ini', 'w') as config_file:
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

        with open(f'config.ini', 'w') as config_file:
            self.config.write(config_file)

    @commands.command(aliases=["svr2"])
    async def setvaultrole2(self, ctx, role: discord.Role):
        '''
        Sets the second role is pinged with withdrawal messages in config.ini
        '''

        if not check_admin(ctx.message.author) and self.config["DEFAULT"]["Superuser"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator. ' \
                                f'This interaction has been logged.'
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to run setvaultrole2, but is not an Administrator',
                self.access)
            return None

        self.config["VAULT"]["Role2"] = str(role.mention)
        log(f'Vault Role 2 has been set to {role.mention}.', self.log_file)

        embed = discord.Embed()
        embed.title = "Vault Role"
        embed.description = f'Vault Role 2 has been set to {role.mention}.'
        await ctx.send(embed=embed)

        with open(f'config.ini', 'w') as config_file:
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

        with open(f'config.ini', 'w') as config_file:
            self.config.write(config_file)

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

        with open(f'config.ini', 'w') as config_file:
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
        Vault Channel: {self.config["VAULT"]["channel"]}
        Vault Channel 2: {self.config["VAULT"]["channel2"]}
        Vault Role: {self.config["VAULT"]["role"]}
        Vault Role 2: {self.config["VAULT"]["role2"]}'''

        await ctx.send(embed=embed)

    @commands.command()
    async def setkey(self, ctx, arg):
        '''
        Sets the secondary Torn API key
        '''

        if not check_admin(ctx.message.author) and self.config["DEFAULT"]["Superuser"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator. ' \
                                f'This interaction has been logged.'
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to run setkey, but is not an Administrator', self.access)
            return None

        self.config["DEFAULT"]["TornAPIKey2"] = str(arg)
        log(f'{ctx.message.author.name} has set the secondary Torn API Key.', self.log_file)

        embed = discord.Embed()
        embed.title = "Torn API Key"
        embed.description = f'The Torn API key for the secondary faction has been set by {ctx.message.author.name}.'
        await ctx.send(embed=embed)

        await ctx.message.delete()

        with open(f'config.ini', 'w') as config_file:
            self.config.write(config_file)
