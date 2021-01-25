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


class Moderation(commands.Cog):
    def __init__(self, config, log_file):
        self.config = config
        self.log_file = log_file

    @commands.command(pass_context=True)
    async def purge(self, ctx, nummessages: int):
        '''
        Purges specified number of messages in the channel the command is invoked in
        '''

        if not check_admin(ctx.message.author) and self.config["DEFAULT"]["Superuser"] != str(ctx.message.author.id):
            embed = discord.Embed()
            embed.title = "Permission Denied"
            embed.description = f'This command requires {ctx.message.author.name} to be an Administrator. ' \
                                f'This interaction has been logged.'
            await ctx.send(embed=embed)

            log(f'{ctx.message.author.name} has attempted to run purge, but is not an Administrator.', self.log_file)
            return None

        await ctx.message.delete()
        await ctx.message.channel.purge(limit=nummessages, check=None, before=None)
        log(f'{nummessages} messages in {ctx.message.channel.name} have been purged by {ctx.message.author.mention}.',
            self.log_file)
        await ctx.send(f'{nummessages} messages have been purged by {ctx.message.author.mention}.')
