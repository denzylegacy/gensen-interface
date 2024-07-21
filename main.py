import discord
from discord.message import Message
from dotenv import load_dotenv
import pytz
import asyncio
import datetime
import traceback
from discord.ext import commands
from discord.enums import ActivityType
from local_io import JSONHandler
from infra import log, DISCORD_TOKEN

load_dotenv()


member_timezone = pytz.timezone("America/Sao_Paulo")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.reactions = True
intents.members = True

data_options = JSONHandler().read_options_json("./infra/options.json")


class Gensen(commands.Bot):
    """Gensen
    """
    def __init__(self, *, intents: discord.Intents, application_id: int):
        super().__init__(command_prefix=data_options["bot_configs"]["prefix"], intents=intents,
                         application_id=application_id)

    async def setup_hook(self):
        cogs = [
            "sources.commands.commands",
            "tasks.tasks",
        ]

        for cog in cogs:
            await self.load_extension(cog)
            log.info(f"Cog {cog} loaded!")

    async def on_ready(self):
        await self.change_presence(
            activity=discord.Activity(
                type=ActivityType.watching,
                name=data_options["bot_configs"]["activity"]
            )
        )

        log.info(f"Client logged in as {self.user} ID: {self.user.id}")

    async def on_message(self, message: Message, /) -> None:
        await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        if not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=True)
        
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("> Comando não encontrado!!", ephemeral=True)
        elif isinstance(error, commands.CommandOnCooldown):
            retry_after = error.retry_after  # Tempo restante em segundos
            tempo_restante = datetime.timedelta(seconds=retry_after)

            dias = tempo_restante.days
            horas, resto_segundos = divmod(tempo_restante.seconds, 3600)
            minutos, segundos = divmod(resto_segundos, 60)

            mensagem = f"> This command is on cooldown! Please try again in {dias} days, {horas} hours, {minutos} minutes and {segundos} seconds."
            await ctx.send(mensagem, ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("> You do not have permission to use this command! 😪", ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("> I don't have permission to run this command! 😪", ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("> Please send all arguments! Type ``/help command`` to view the command details.",
                           ephemeral=True)
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("> Esse comando não existe! Use ``/help`` para ver a lista completa de comandos.",
                           ephemeral=True)
        elif isinstance(error, commands.MessageNotFound):
            await ctx.send("> Message not found 😪", ephemeral=True)

        elif isinstance(error, commands.CheckFailure):
            await ctx.send("This command is only available to verified members!!", ephemeral=True)
        else:
            log_channel = ctx.guild.get_channel(
                data_options["bot_configs"]["channel_bot_erro"])

            traceback_message = "".join(traceback.format_exception(None, error, error.__traceback__))
            await log_channel.send(f'> **Unexpected error:**\n```\n{traceback_message[:1800]}\n```')


bot = Gensen(intents=intents, application_id=data_options["bot_configs"]["client_id"])


async def main():
    async with bot:
        bot.member_timezone = member_timezone
        await bot.start(DISCORD_TOKEN)


asyncio.run(main())
