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

import datetime
from decimal import Decimal
import re


def num_to_text(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def text_to_num(text):
    decimal = {
        'K': 3,
        "M": 6,
        "B": 9
    }

    text = text.upper()
    if text[-1] in decimal:
        num, magnitude = text[:-1], text[-1]
        return Decimal(num) * 10 ** decimal[magnitude]
    else:
        return Decimal(text)


def check_admin(member):
    return True if member.guild_permissions.administrator else False


def remove_torn_id(name):
    return re.sub("[\(\[].*?[\)\]]", "", name)[:-1]


def log(message, file):
    file.write(str(datetime.datetime.now()) + " -- " + message + "\n")
    file.flush()


def commas(number):
    return "{:,}".format(number)
