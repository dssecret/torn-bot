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

import json

jsons = ["guilds", "vault"]


def _read(file):
    with open(f'{file}.json') as file:
        return json.load(file)


def _write(file, data):
    with open(f'{file}.json', 'w') as file:
        json.dump(data, file, indent=4)


def initialize():
    try:
        file = open("guilds.json")
        file.close()
    except FileNotFoundError:
        bottoken = input("Please input the bot token: ")
        data = {
            "bottoken": bottoken,
            "masterapikey": "",
            "superuser": 0,
            "prefix": "?",
            "guilds": []
        }
        _write("guilds", data)

    try:
        file = open("vault.json")
        file.close()
    except FileNotFoundError:
        _write("vault", {})


def read(file):
    if file in jsons:
        return _read(file)
    else:
        raise ValueError("Illegal File Name")


def write(file, data):
    if file in jsons:
        _write(file, data)
    else:
        raise ValueError("Illegal File Name")


def get_guild(guildid, key=None):
    for guild in read("guilds")["guilds"]:
        if str(guild["id"]) == str(guildid):
            if key is None:
                return guild
            else:
                return guild[key]


def get_vault(guildid, key=None):
    return read("vault")[str(guildid)] if key is None else read("vault")[str(guildid)][key]


def get_superuser():
    return read("guilds")["superuser"]
