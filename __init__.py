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

import sys
import asyncio
import logging

import vault
import admin
import moderation
import superuser
import torn
from required import *
import dbutils

assert sys.version_info >= (3, 6), "requires Python %s.%s or newer" % (3, 6)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

dbutils.initialize()

guilds = dbutils.read("guilds")
vaults = dbutils.read("vault")
# users = dbutils.read("users")

client = discord.client.Client()
intents = discord.Intents.default()
intents.reactions = True
intents.members = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix=get_prefix, help_command=None, intents=intents)
file = open(f'log.txt', "a")
access = open(f'access.txt', "a")


@bot.event
async def on_ready():
    guild_count = 0

    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count = guild_count + 1

        for jsonguild in guilds["guilds"]:
            if jsonguild["id"] == str(guild.id):
                break
        else:
            guilds["guilds"].append({
                "id": str(guild.id),
                "prefix": "?",
                "tornapikey": "",
                "tornapikey2": ""
            })
            dbutils.write("guilds", guilds)
        if str(guild.id) not in vaults:
            vaults[guild.id] = {
                "channel": "",
                "role": "",
                "channel2": "",
                "role2": "",
                "banking": ""
            }
            dbutils.write("vault", vaults)
        #
        # for member in guild.members:
        #     if member.id in users:
        #         continue
        #     if member.bot:
        #         continue
        #     users[member.id] = {
        #         "tornid": "",
        #         "tornapikey": "",
        #         "generaluse": False
        #     }
        #     dbutils.write("users", users)

    print(f'Bot is in {guild_count} guilds.')

    bot.add_cog(vault.Vault(bot, file))
    bot.add_cog(admin.Admin(file, bot, client, access))
    bot.add_cog(moderation.Moderation(file, access))
    bot.add_cog(superuser.Superuser(client, file, bot, access))
    bot.add_cog(torn.Torn(file, bot, client, access))


@bot.event
async def on_guild_join(guild):
    embed = discord.Embed()
    embed.title = f'Welcome to {bot.user.display_name}'
    embed.description = f'Thank you for inviting {bot.user.display_name} to your server'
    embed.add_field(name="Help", value="`?help` or contact <@dssecret#0001> on Discord, on ds_secret [2383326] on Torn,"
                                       " or dssecret on Github")
    embed.add_field(name="How to Setup", value="Run admin commands that can be found in the [Wiki]"
                                               "(https://github.com/dssecret/torn-bot/wiki) under [Commands]"
                                               "(https://github.com/dssecret/torn-bot/wiki/Commands).")

    await guild.text_channels[0].send(embed=embed)


@bot.event
async def on_message(message):
    if message.author.bot:
        return None
    if str(message.channel.id) == dbutils.read("vault")[str(message.guild.id)]["banking"] \
            and message.clean_content[0] != get_prefix(client, message):
        await message.delete()
        embed = discord.Embed()
        embed.title = "Bot Channel"
        embed.description = "This channel is only for vault withdrawals. Please do not post any other messages in" \
                            " this channel."
        message = await message.channel.send(embed=embed)
        await asyncio.sleep(30)
        await message.delete()

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed()
        embed.title = "Cooldown"
        embed.description = f'You are on cooldown. Please try again in {round(error.retry_after, 2)} seconds.'
        await ctx.send(embed=embed)
        if ctx.message.channel.id == dbutils.get_vault(ctx.guild.id, "banking"):
            await asyncio.sleep(30)
            await ctx.message.delete()


@bot.command()
@commands.cooldown(1, 5, commands.BucketType.guild)
async def ping(ctx):
    '''
    Shows the ping to the server
    '''

    latency = bot.latency
    log(f'Latency: {latency}', file)

    embed = discord.Embed()
    embed.title = "Latency"
    embed.description = f'{latency} seconds'
    await ctx.send(embed=embed)


@bot.command()
@commands.cooldown(1, 30, commands.BucketType.guild)
async def prefix(ctx):
    '''
    Returns the prefix for the bot
    '''

    embed = discord.Embed()
    embed.title = "Bot Prefix"
    embed.description = f'The bot prefix is {get_prefix(bot, ctx.message)}.'
    await ctx.send(embed=embed)


@bot.command()
@commands.cooldown(1, 30, commands.BucketType.guild)
async def version(ctx):
    '''
    Returns the current version of the bot
    '''

    embed = discord.Embed()
    embed.title = "Version"
    embed.description = "v1.3 Pre-Release 5 In-Dev"
    await ctx.send(embed=embed)


@bot.command()
@commands.cooldown(1, 30, commands.BucketType.guild)
async def license(ctx):
    '''
    Returns the copyright of the bot's software.
    '''

    embed = discord.Embed()
    embed.title = "License: Affero General Public License v3"
    embed.description = "torn-bot is free software: you can redistribute it and/or modify it under the terms of " \
                        "the GNU Affero General Public License as published by the Free Software Foundation, either" \
                        " version 3 of the License, or (at your option) any later version. torn-bot is distributed in" \
                        " the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied " \
                        "warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero " \
                        "General Public License for more details. You should have received a copy of the GNU" \
                        " General Public License along with torn-bot.  If not, see <https://www.gnu.org/licenses/>."
    embed.add_field(name="Full License", value="A full version of the license can also be found in the [GitHub"
                                               " repository](https://github.com/dssecret/torn-bot/blob/main/LICENSE).")
    embed.add_field(name="License Repercussions", value="Due to the license used for this project, all forks,"
                                                        " clones, and hosted versions of this project must include "
                                                        "this same license (the Affero General Public License v3)."
                                                        " Additionally, hosted versions must have a method for the"
                                                        " user to retrieve the source code from the hosted "
                                                        "versions' server(s). For more information on the AGPL"
                                                        " v3 license, check out GNU's [license page]"
                                                        "(https://www.gnu.org/licenses/).")
    await ctx.send(embed=embed)


@bot.command()
@commands.cooldown(1, 30, commands.BucketType.guild)
async def help(ctx, arg=None):
    '''
    Returns links to the documentation, issues, developer contact information, and other pages if no command is passed
    as a paramter. If a command is passed as a paramter, the help command returns the help message of the passed
    command.
    '''

    embed = discord.Embed()
    command_list = [command.name for command in bot.commands]

    if not arg:
        embed = None
        page1 = discord.Embed(
            title='Useful Resources',
            description=f'Server: {ctx.guild.name}\nPrefix: {ctx.prefix}'
        ).set_footer(text="Page 1/4")
        page2 = discord.Embed(
            title='Vault Commands',
        ).set_footer(text="Page 2/4")
        page3 = discord.Embed(
            title='Admin Commands',
            description='Ha! You think I\'d share the admin commands with you. If you\'re really an admin on the server'
                        ', check out the commands in my docs.'
        ).set_footer(text="Page 3/4")
        page4 = discord.Embed(
            title="Miscellaneous Commands"
        ).set_footer(text="Page 4/4")

        page1.description = f'Server: {ctx.guild.name}\nPrefix: {ctx.prefix}'
        page1.add_field(name="GitHub Repository", value="https://github.com/dssecret/torn-bot")
        page1.add_field(name="GitHub Issues", value="https://github.com/dssecret/torn-bot/issues")
        page1.add_field(name="Documentation (Under Construction)", value="https://github.com/dssecret/torn-bot/wiki")
        page1.add_field(name="Torn City User", value="https://www.torn.com/profiles.php?XID=2383326")
        page1.add_field(name="Discord User", value="dssecret#8137")
        page1.add_field(name="For More Information", value="Please contact me (preferably on Discord or Github).")

        page2.add_field(name="`?withdraw [value]`", value="Sends a request to withdraw the passed amount of money to "
                                                          "the banker")
        page2.add_field(name="`?bal`", value="Returns your full balance in the faction vault.")
        page2.add_field(name="`?b`", value="Returns a simplified version of your balance in the faction vault.")

        page4.add_field(name="`?prefix`", value="Returns the bot's current prefix.")
        page4.add_field(name="`?version`", value="Returns the bot's current version (assuming I remember to change "
                                                "it before I release it).")
        page4.add_field(name="`?license`", value="Returns the license of the bot's software.")

        pages = [page1, page2, page3, page4]

        message = await ctx.send(embed = page1)
        await message.add_reaction('⏮')
        await message.add_reaction('◀')
        await message.add_reaction('▶')
        await message.add_reaction('⏭')

        def check(reaction, user):
            return user == ctx.author

        i = 0
        reaction = None

        while True:
            if str(reaction) == '⏮':
                i = 0
                await message.edit(embed=pages[i])
            elif str(reaction) == '◀':
                if i > 0:
                    i -= 1
                    await message.edit(embed=pages[i])
            elif str(reaction) == '▶':
                if i < 3:
                    i += 1
                    await message.edit(embed=pages[i])
            elif str(reaction) == '⏭':
                i = 3
                await message.edit(embed=pages[i])

            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
                await message.remove_reaction(reaction, user)
            except:
                break

        await message.clear_reactions()
    elif arg in command_list:
        embed.add_field(name=arg, value=bot.get_command(arg).help)
    else:
        embed.description = "This command does not exist."

    if embed is not None:
        await ctx.send(embed=embed)


if __name__ == "__main__":
    bot.run(dbutils.read("guilds")["bottoken"])
    file.close()
