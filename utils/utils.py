import random
import re
import discord


class Utils:
    def __init__(self, client: discord.Client = None) -> None:
        self.client = client

    def random_discord_color(self):
        return discord.Colour(random.randint(0, 0xFFFFFF))

    def extract_startwith(self, text: str) -> str:
        parts = text.split(' -> ')
        if parts[0].startswith('/'):
            return parts[0]

    def extract_numbers(self, text):
        return re.sub('[^0-9]', '', text)

    def genList(self, myList):
        for n in myList:
            yield n

    def format_seconds_time(self, time):
        hours, remainder = divmod(time, 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        year, days = divmod(days, 365)

        return year, days, hours, minutes, seconds

    def datatime_time(self, timeout__, timein__):
        duration = timeout__ - timein__

        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        year, days = divmod(days, 365)


class Utilities():
    def __init__(self, **kwargs) -> None:
        self.bot = kwargs.get("bot")
        
    def textstyle(self, text:str=None) -> list:
            if text is None: return None
            if 'long' in text.lower(): return [discord.TextStyle.long, 300]
            if 'short' in text.lower(): return [discord.TextStyle.short, 100]
            return [text, None]

    def formating(self, text:str=None) -> list:
        if text is None: return None
        str1 = re.sub('[a-z]*=', '', text)
        str2 = str1.replace('\"', '').split(',')
        str3 = []
        for word in str2:
            str3.append(word.strip())
        del str1, str2
        return str3
