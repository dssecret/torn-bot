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


class Admin(commands.Cog):
    def __init__(self, config, log_file, bot, client):
        self.config = config
        self.log_file = log_file
        self.bot = bot
        self.client = client

    @commands.command(aliases=["svc"])
    async def setvaultchannel(self, ctx):
        '''
        Sets the channel that withdrawal messages are sent to in config.ini
        '''

        if not check_admin(ctx.message.author) and ctx.message.author.id == self.config["DEFAULTS"]["superuser"]:
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
        Sets the role is pinged with withdrawal messages in config.ini
        '''

        if not check_admin(ctx.message.author) and ctx.message.author.id == self.config["DEFAULTS"]["superuser"]:
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
        Sets the prefix for the bot in config.ini
        '''

        if not check_admin(ctx.message.author) and ctx.message.author.id == self.config["DEFAULTS"]["superuser"]:
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

    @commands.command(aliases=["snr"])
    async def setnoobrole(self, ctx, role: discord.Role):
        '''
        Sets the role given to users under level 15 in config.ini
        '''

        if not check_admin(ctx.message.author) and ctx.message.author.id == self.config["DEFAULTS"]["superuser"]:
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = "This command requires the sender to be an Administrator. " \
                                "This interaction has been logged."
            await ctx.send(embed=embed)

            log(ctx.message.author + " has attempted to run setnoobrole, but is not an Administrator.", self.log_file)
            return None

        self.config["ROLES"]["Noob"] = str(role.id)
        log("Noob Role has been set to " + self.config["ROLES"]["Noob"] + ".", self.log_file)

        embed = discord.Embed()
        embed.title = "Noob Role"
        embed.description = "Noob Role has been set to " + role.name + "."
        await ctx.send(embed=embed)

        with open('config.ini', 'w') as config_file:
            self.config.write(config_file)

    @commands.command()
    async def runnoob(self, ctx):
        '''
        Adds the noob role from all users under level 15. Removes the noob role from all users who have the noob role,
        but are above level 15.
        '''

        if not check_admin(ctx.message.author) and ctx.message.author.id == self.config["DEFAULTS"]["superuser"]:
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = "This command requires the sender to be an Administrator. " \
                                "This interaction has been logged."
            await ctx.send(embed=embed)

            log(ctx.message.author + " has attempted to run runnoob, but is not an Administrator.", self.log_file)
            return None

        response = requests.get('https://api.torn.com/faction/?selections=&key=' +
                                str(self.config["DEFAULT"]["TornAPIKey"]))
        log("The Torn API has responded with HTTP status code " + str(response.status_code) + ".", self.log_file)

        members = list(response.json()["members"].keys())

        for member in members:
            request = requests.get('https://api.torn.com/user/' + member + "?selections=basic,discord&key=" +
                                   str(self.config["DEFAULT"]["TornAPIKey"]))
            log("The Torn API has responded with HTTP status code " + str(request.status_code) + ".", self.log_file)

            discordid = request.json()["discord"]["discordID"]
            if discordid == "":
                continue

            discord_member = self.bot.get_guild(int(self.config["DEFAULT"]["serverid"])).get_member(int(discordid))
            noob = ctx.guild.get_role(int(self.config["ROLES"]["noob"]))

            if discord_member is None:
                continue

            if request.json()["level"] <= 15:
                await discord_member.add_roles(noob)
                await ctx.send("The Noob role has been added to " + str(discord_member) + ".")
                log("The Noob role has been added to " + str(discord_member) + ".", self.log_file)
            else:
                if noob in discord_member.roles:
                    await discord_member.remove_roles(noob)
                    await ctx.send("The Noob role has been removed from " + str(discord_member) + ".")
                    log("The Noob role has been removed from " + str(discord_member) + ".", self.log_file)
