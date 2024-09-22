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
        self.messengers: list = ["gensen", "keyripper"]

    @commands.Cog.listener()
    async def on_ready(self):
        await self.background_tasks.start()

    async def messages(self):
        log.info(f"[background_tasks] messages: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        firebase = Firebase()
        
        connection = firebase.firebase_connection("root")

        users = connection.child("users").get()
        
        if not users:
            return
        
        for user in users.keys():
            for messenger in self.messengers:
                user_messages = connection.child(f"users/{user}/messages")
                
                if not user_messages.get():
                    return
                
                for message in user_messages.key():
                    ### DM NOTIFICATION ###
    
                    log.info(f"[NOTIFYING {user}]: {message}")
                    
                    embed = discord.Embed(
                        title=message["title"],
                        description=message["description"],
                        color=0xffa07a
                    )
    
                    embed.add_field(
                        name="",
                        value="If you believe this is a mistake, please contact my developer!",
                        inline=False
                    )
    
                    await self.bot.get_user(int(user)).send(embed=embed)
    
                    connection.child(message).delete()

    @tasks.loop(seconds=60)
    async def background_tasks(self):
        await self.messages()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BackgroundTasks(bot))
