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


class Torn(commands.Cog):
    def __init__(self, config, log_file, bot, client, server, access):
        self.config = config
        self.log_file = log_file
        self.bot = bot
        self.client = client
        self.server = server
        self.access = access

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def addid(self, ctx, id:int):
        if self.config.has_option("ID", str(ctx.message.author.id)):
            embed = discord.Embed()
            embed.title = "ID Already Set"
            embed.description = "Your ID is already set in the database."
            await ctx.send(embed=embed)
            return None

        request = requests.get(f'https://api.torn.com/user/{id}?selections=discord&key='
                               f'{self.config["DEFAULT"]["TornAPIKey"]}')
        if request.status_code != 200:
            embed = discord.Embed()
            embed.title = "Error"
            embed.description = f'Something has possibly gone wrong with the request to the Torn API with HTTP status' \
                                f' code {request.status_code} has been given at {datetime.datetime.now()}.'
            await ctx.send(embed=embed)

            log(f'The Torn API has responded with HTTP status code {request.status_code}.', self.log_file)
            return None

        if request.json()["discord"]["discordID"] == "":
            embed = discord.Embed()
            embed.title = "ID Not Set"
            embed.description = "Your Discord ID is not set in the Torn database. To set your Discord ID in the Torn" \
                                "database, visit the official Torn Discord server and verify yourself."
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to set id, but is not verified in the official Discord '
                f'server.', self.log_file)
            return None

        self.config["ID"][str(ctx.message.author.id)] = request.json()["discord"]["discordID"]
        embed = discord.Embed()
        embed.title = "ID Set"
        embed.description = "Your ID has been set in the database."
        await ctx.send(embed=embed)

        log(f'{ctx.message.author.name} has set their id which is {id}.', self.log_file)

        with open(f'config.ini', 'w') as config_file:
            self.config.write(config_file)
