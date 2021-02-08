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
        self.configuration = config
        self.log_file = log_file
        self.bot = bot
        self.client = client
        self.server = server
        self.access = access

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def config(self, ctx, arg=None, value=None):
        '''
        Returns the current configuration of the bot
        '''

        if not check_admin(ctx.message.author) and self.configuration["DEFAULT"]["Superuser"] != \
                str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator. ' \
                                f'This interaction has been logged.'
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to run config, but is not an Administrator', self.access)
            return None

        embed = discord.Embed()

        if not arg:
            embed.title = "Current Configuration"
            embed.description = f'''Torn API Key: Classified
            Bot Token: Classified
            Prefix: {self.configuration["DEFAULT"]["Prefix"]}
            Server ID: {self.configuration["DEFAULT"]["serverid"]}
            Superuser: {self.configuration["DEFAULT"]["Superuser"]}
            Vault Channel: {self.configuration["VAULT"]["channel"]}
            Vault Channel 2: {self.configuration["VAULT"]["channel2"]}
            Vault Role: {self.configuration["VAULT"]["role"]}
            Vault Role 2: {self.configuration["VAULT"]["role2"]}
            Banking Channel: {self.configuration["VAULT"]["banking"]}
            Noob Role: {self.configuration["ROLES"]["Noob"]}
            Users Over Level 15: {self.configuration["DEFAULT"]["over15"]}'''
        elif arg == "guild":
            self.configuration["DEFAULT"]["serverid"] = str(ctx.guild.id)
            log(f'The server ID has been set to {ctx.guild.id}.', self.log_file)
            embed.title = "Server ID"
            embed.description = f'The server ID has been set to {ctx.guild.id}.'
        # Configurations that require a value below here
        elif not value:
            embed.title = "Value Error"
            embed.description = "A value must be passed"
        elif arg == "vc":
            for channel in self.server.channels:
                if str(channel.id) != value[2:-1]:
                    continue
                self.configuration["VAULT"]["Channel"] = channel.name
                log(f'Vault Channel has been set to {self.configuration["VAULT"]["Channel"]}.', self.log_file)
                embed.title = "Vault Channel"
                embed.description = f'Vault Channel has been set to {self.configuration["VAULT"]["Channel"]}.'
        elif arg == "vc2":
            for channel in self.server.channels:
                if str(channel.id) != value[2:-1]:
                    continue
                self.configuration["VAULT"]["Channel2"] = channel.name
                log(f'Vault Channel 2 has been set to {self.configuration["VAULT"]["Channel2"]}.', self.log_file)
                embed.title = "Vault Channel 2"
                embed.description = f'Vault Channel 2 has been set to {self.configuration["VAULT"]["Channel2"]}.'
        elif arg == "vr":
            for role in self.server.roles:
                if role.mention != value:
                    continue
                self.configuration["VAULT"]["Role"] = str(role.mention)
                log(f'Vault Role has been set to {role.mention}.', self.log_file)
                embed.title = "Vault Role"
                embed.description = f'Vault Role has been set to {role.mention}.'
        elif arg == "vr2":
            for role in self.server.roles:
                if role.mention != value:
                    continue
                self.configuration["VAULT"]["Role2"] = str(role.mention)
                log(f'Vault Role 2 has been set to {role.mention}.', self.log_file)
                embed.title = "Vault Role 2"
                embed.description = f'Vault Role 2 has been set to {role.mention}.'
        elif arg == "prefix":
            self.configuration["DEFAULT"]["Prefix"] = str(value)
            log(f'Bot Prefix has been set to {value}.', self.log_file)
            embed.title = "Bot Prefix"
            embed.description = f'Bot Prefix has been set to {value}. The bot requires a restart for the prefix ' \
                                f'change to go into effect.'
        elif arg == "nr":
            for role in self.server.roles:
                if role.mention != value:
                    continue
                self.configuration["ROLES"]["Noob"] = str(role.id)
                log(f'Noob Role has been set to {role.id}.', self.log_file)
                embed.title = "Noob Role"
                embed.description = f'Noob Role has been set to {role.name}.'
        elif arg == "key":
            self.configuration["DEFAULT"]["TornAPIKey2"] = str(value)
            log(f'{ctx.message.author.name} has set the secondary Torn API Key.', self.log_file)
            embed.title = "Torn API Key"
            embed.description = f'The Torn API key for the secondary faction has been set by {ctx.message.author.name}.'
            await ctx.message.delete()
        elif arg == "bc":
            for channel in self.server.channels:
                if str(channel.id) != value[2:-1]:
                    continue
                self.configuration["VAULT"]["Banking"] = str(channel.id)
                log(f'Banking Channel has been set to {self.configuration["VAULT"]["Banking"]}.', self.log_file)
                embed.title = "Banking Channel"
                embed.description = f'Banking Channel has been set to {self.configuration["VAULT"]["Banking"]}.'
        else:
            embed.title = "Configuration"
            embed.description = "This key is not a valid configuration key."

        await ctx.send(embed=embed)

        with open(f'config.ini', 'w') as config_file:
            self.configuration.write(config_file)
