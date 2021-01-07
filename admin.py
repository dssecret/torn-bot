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
    def __init__(self, config, log_file):
        self.config = config
        self.log_file = log_file

    @commands.command(aliases=["svc"])
    async def setvaultchannel(self, ctx):
        '''
        Sets the channel that withdrawal messages are sent to
        '''

        if not check_admin(ctx.message.author):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = "This command requires the sender to be an Administrator. " \
                                "This interaction has been logged."
            await ctx.send(embed=embed)

            log(ctx.message.author + " has attempted to run setvaultchannel, but is not an Administrator.",
                self.log_file)
            return None

        self.config["VAULT"]["Channel"] = str(ctx.message.channel)
        log("Vault Channel has been set to " + self.config["VAULT"]["Channel"] + ".", self.log_file)

        embed = discord.Embed()
        embed.title = "Vault Channel"
        embed.description = "Vault Channel has been set to " + self.config["VAULT"]["Channel"] + "."
        await ctx.send(embed=embed)

        with open('config.ini', 'w') as config_file:
            self.config.write(config_file)

    @commands.command(aliases=["svr"])
    async def setvaultrole(self, ctx, role: discord.Role):
        '''
        Sets the role is pinged with withdrawal messages
        '''

        if not check_admin(ctx.message.author):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = "This command requires the sender to be an Administrator. " \
                                "This interaction has been logged."
            await ctx.send(embed=embed)

            log(ctx.message.author + " has attempted to run setvaultrole, but is not an Administrator.", self.log_file)
            return None

        self.config["VAULT"]["Role"] = str(role.mention)
        log("Vault Role has been set to " + self.config["VAULT"]["Role"] + ".", self.log_file)

        embed = discord.Embed()
        embed.title = "Vault Role"
        embed.description = "Vault Role has been set to " + self.config["VAULT"]["Role"] + "."
        await ctx.send(embed=embed)

        with open('config.ini', 'w') as config_file:
            self.config.write(config_file)

    @commands.command(aliases=["sp"])
    async def setprefix(self, ctx, arg="?"):
        '''
        Sets the prefix for the bot
        '''

        if not check_admin(ctx.message.author):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = "This command requires the sender to be an Administrator. " \
                                "This interaction has been logged."
            await ctx.send(embed=embed)

            log(ctx.message.author + " has attempted to run setprefix, but is not an Administrator.", self.log_file)
            return None

        self.config["DEFAULT"]["Prefix"] = str(arg)
        log("Bot prefix has been set to " + self.config["DEFAULT"]["Prefix"] + ".", self.log_file)

        embed = discord.Embed()
        embed.title = "Bot Prefix"
        embed.description = "Bot prefix has been set to " + self.config["DEFAULT"]["Prefix"] + \
                            ". The bot requires a restart for the prefix change to go into effect."
        await ctx.send(embed=embed)

        with open('config.ini', 'w') as config_file:
            self.config.write(config_file)
