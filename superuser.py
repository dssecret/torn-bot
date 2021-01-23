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

import subprocess
import random


class Superuser(commands.Cog):
    def __init__(self, client, config, log_file, bot):
        self.client = client
        self.config = config
        self.log_file = log_file
        self.bot = bot

    def is_superuser(self, id):
        return True if self.config["DEFAULT"]["Superuser"] == str(id) else False

    @commands.command()
    async def shutdown(self, ctx):
        '''
        Shuts down the bot
        '''

        embed = discord.Embed(colour=random.randint(0, 16777215))

        if not self.is_superuser(ctx.message.author.id):
            embed.title = "Permission Denied"
            embed.description = f'{ctx.message.author.name} is not the superuser. This incident will be reported.'
            log(f'{ctx.message.author.name} attempted to shutdown the bot, but is not the superuser.', self.log_file)
            await ctx.send(embed=embed)
            return None

        embed.title = "Bot Shutdown"
        embed.description = "The bot has been shutdown. The bot will need to be manually started."

        await ctx.send(embed=embed)
        await exit(0)

    @commands.command()
    async def restart(self, ctx):
        '''
        Restarts the bot
        '''

        embed = discord.Embed(colour=random.randint(0, 16777215))

        if not self.is_superuser(ctx.message.author.id):
            embed.title = "Permission Denied"
            embed.description = f'{ctx.message.author.name} is not the superuser. This incident will be reported.'
            log(f'{ctx.message.author.name} is not the superuser. This incident will be reported.', self.log_file)
            await ctx.send(embed=embed)
            return None

        embed.title = "Bot Restart"
        embed.description = "The bot is being restarted."
        await ctx.send(embed=embed)

        subprocess.Popen(['python3', '__init__.py', '&'])
        await exit(0)
