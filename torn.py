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


class Torn(commands.Cog):
    def __init__(self, log_file, bot, client, access):
        self.log_file = log_file
        self.bot = bot
        self.client = client
        self.access = access

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def addid(self, ctx, id:int):
        if dbutils.get_user(ctx.message.author.id)["tornid"] != "":
            embed = discord.Embed()
            embed.title = "ID Already Set"
            embed.description = "Your ID is already set in the database."
            await ctx.send(embed=embed)
            return None

        request = await tornget(ctx, f'https://api.torn.com/user/{id}?selections=discord&key=')

        if request["discord"]["discordID"] == "":
            embed = discord.Embed()
            embed.title = "ID Not Set"
            embed.description = "Your Discord ID is not set in the Torn database. To set your Discord ID in the Torn" \
                                "database, visit the official Torn Discord server and verify yourself."
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to set id, but is not verified in the official Discord '
                f'server.', self.log_file)
            return None

        if request["discord"]["discordID"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Invalid ID"
            embed.description = f'Your Discord ID is not the same as the Discord ID stored in Torn\'s' \
                                f' database for your given Torn ID.'
            await ctx.send(embed=embed)
            log(f'{ctx.message.author.name} has attempted to set their Torn ID to be {id}, but their Discord ID '
                f'({ctx.message.author.id} does not match the value in Torn\'s DB.', self.log_file)
            return None

        data = dbutils.read("users")
        data[str(ctx.message.author.id)]["tornid"] = str(id)
        dbutils.write("users", data)

        embed = discord.Embed()
        embed.title = "ID Set"
        embed.description = "Your ID has been set in the database."
        await ctx.send(embed=embed)
        log(f'{ctx.message.author.name} has set their id which is {id}.', self.log_file)
