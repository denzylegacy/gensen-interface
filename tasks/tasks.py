import discord
from discord.ext import commands, tasks
import datetime

from infra import log
from firebase import Firebase


class BackgroundTasks(commands.Cog):
    """BackgroundTasks
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.background_tasks.start()

    async def market_conditions_evaluator(self):
        log.info(f"[background_tasks] market_conditions_evaluator: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        firebase = Firebase()
        
        connection = firebase.firebase_connection("root")

        users = connection.child("users").get()

        if not users:
            return

        for user in users.keys():
            user_gensen_messages = connection.child(f"users/{user}/messages/gensen")
            
            if not user_gensen_messages.get():
                return
        
            for message in users[user]["messages"]["gensen"].keys():
                ### DM NOTIFICATION ###

                log.info(f"[INSTANT ORDER NOTIFICATION] {message} -> {user}")
                
                embed = discord.Embed(
                    title=users[user]["messages"]["gensen"][message]["title"],
                    description=users[user]["messages"]["gensen"][message]["description"],
                    color=0xffa07a
                )

                embed.add_field(
                    name="",
                    value="If you believe this is a mistake, please contact my developer!",
                    inline=False
                )

                await self.bot.get_user(int(user)).send(embed=embed)

                connection.child(f"users/{user}/messages/gensen/{message}").delete()

    @tasks.loop(seconds=60)
    async def background_tasks(self):
        await self.market_conditions_evaluator()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BackgroundTasks(bot))
