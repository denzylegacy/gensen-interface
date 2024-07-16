import discord
from discord.ext import commands, tasks
import asyncio
import datetime
import pytz
from pathlib import Path


class Monitoring(commands.Cog):
    """Works with Monitoring"""

    def __init__(self, bot):
        self.bot = bot
        self.current_dir = Path(__file__).resolve().parent

    @commands.Cog.listener()
    async def on_ready(self):
        await self.background_tasks.start()

    async def background(self, forced_execution: bool = False):
        date_time = datetime.datetime.now(
            pytz.timezone("America/Sao_Paulo")
        ).strftime("%d-%m-%Y às %H:%M:%S")


        if "23:09:" in str(date_time) or forced_execution:  # 19:00: / 09:30:

            successful_attempt = False
            errors = None

            print(f"({date_time}) running code...")
            notification_channel = self.bot.get_channel(1262585672787824703)

            for attempt in range(4):
                if not successful_attempt:
                    try:
                        # coins = await engine()
                        coins = []

                        embed = discord.Embed(
                            title="Monitoramento SOS",
                            description=f"``{date_time.split(' ')[0]}`` "
                                        f"https://www.coingecko.com/\n\n",
                            color=0xffa07a
                        )

                        for coin in coins:
                            dou_hierarquia_join, title_marker, abstract_marker, title_marker_url = coin

                            embed.add_field(
                                name=f"{title_marker}",
                                value="> {}...".format(abstract_marker.replace(title_marker, "").strip()[:270]),
                                inline=False
                            )

                            embed.add_field(
                                name="Fonte",
                                value=f"{dou_hierarquia_join.split(' > ')[-1:][0]}",
                            )

                            embed.add_field(
                                name="URL",
                                value=f"[www.in.gov.br/web/dou/...]({title_marker_url})",
                            )

                            embed.add_field(
                                name="\n\n", value="\n\n", inline=False
                            )

                        if len(coins) > 0:
                            embed.add_field(
                                name="Pass!",
                                value="Pass!",
                                inline=False
                            )
                        else:
                            embed.add_field(
                                name=f"Não há novidades!",
                                value="Fique atento! Pode haver alguma coisa na próxima verificação...",
                                inline=False
                            )

                        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                        embed.set_footer(
                            text=f"Notificado com ♥ por {self.bot.user.name} - "
                                 f"Copyright © 2023",
                            icon_url=self.bot.user.avatar.url)

                        if len(coins) > 0 or "20:00:" not in str(date_time):
                            await asyncio.sleep(1)
                            await notification_channel.send(embed=embed)
                        successful_attempt = True
                        await asyncio.sleep(30)

                    except Exception as error:
                        errors = error
                        print(f"ERROR: {error}")
            if not successful_attempt:
                if len(str(errors)) < 3000:
                    await asyncio.sleep(1)
                    await self.bot.get_channel(1124703584961974417).send(
                        f"> ``{date_time}`` Hm... um bug ocorreu durante o monitoramento... 😢\n"
                        f"```ERROR LOG: {errors[:350]}...```")

    @tasks.loop(seconds=30)
    async def background_tasks(self, forced_execution: bool = False):

        def day_of_the_week():
            week_days = [
                "monday", "tuesday", "wednesday",
                "thursday", "friday", "saturday", "sunday"
            ]
            return str(week_days[datetime.datetime.now().weekday()])

        today = day_of_the_week()

        if today != "saturday" and today != "sunday" or forced_execution:
            await self.background(forced_execution=forced_execution)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Monitoring(bot))
