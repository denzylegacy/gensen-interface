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
                user_messages = connection.child(f"users/{user}/messages/{messenger}")
                
                if not user_messages.get():
                    continue
            
                for message in users[user]["messages"][messenger].keys():
                    ### DM NOTIFICATION ###
    
                    log.info(f"[NOTIFYING {user}]: {message}")
                    
                    embed = discord.Embed(
                        title=users[user]["messages"][messenger][message]["title"],
                        description=users[user]["messages"][messenger][message]["description"],
                        color=0xffa07a
                    )
    
                    embed.add_field(
                        name="",
                        value="If you believe this is a mistake, please contact my developer!",
                        inline=False
                    )
    
                    await self.bot.get_user(int(user)).send(embed=embed)
    
                    connection.child(f"users/{user}/messages/{messenger}/{message}").delete()


    @tasks.loop(seconds=60)
    async def background_tasks(self):
        try:
            await self.messages()
        except Exception as error:
            print(error)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BackgroundTasks(bot))
