import discord
from discord.message import Message
from pprint import pprint
from dotenv import load_dotenv
import pytz
import asyncio
import datetime
import traceback
from discord.ext import commands
from discord.enums import ActivityType

from local_io import JSONHandler
from infra import log, DISCORD_TOKEN
from coingecko import Coingecko

load_dotenv()


member_timezone = pytz.timezone("America/Sao_Paulo")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.reactions = True
intents.members = True

data_options = JSONHandler().read_options_json("./infra/options.json")


class ゲンセン(commands.Bot):
    """Gensen -Golden Fountain-
    # https://discord.com/oauth2/authorize?client_id=1205621013417693205

    - Sell for every R$5.00 of profit (This value may be changed after future analysis.)
    - Supply:
      - Think about what the issue of gas depletion will be like (As with each sale the value of the crypto will be reduced)
    - Perform automatic analysis for low supply suggestion per token
    - Cover the initial cost invested
    - Obtain at least half of the capital invested apart from covering the same amount

    Considerations:
    * It must be necessary to input the assets and values for the assets
    for each sale, the machine must request confirmation of the sale, as long as the Coinbase API is not implemented
    This is to avoid problems (I'm sorry and I'm not going to explain them now...)

    * The user must be notified when to make the sale and purchase, and which assets
    * Create a watch list, so as soon as an asset falls below a certain percentage,
    a purchase notification is made
    """
    def __init__(self, *, intents: discord.Intents, application_id: int):
        super().__init__(command_prefix=data_options["bot_configs"]["prefix"], intents=intents,
                         application_id=application_id)
        self.remove_command("help")
        # self.help_command = HelpCommand()

    async def setup_hook(self):
        cogs = [
            'sources.commands.commands',
            # 'sources.reactions',
            # 'sources.automations.tasks',
        ]

        for cog in cogs:
            await self.load_extension(cog)
            log.info(f'Cog {cog} loaded!')

    async def on_ready(self):
        await self.change_presence(
            activity=discord.Activity(
                type=ActivityType.watching,
                name="Trading"
            )
        )

        try:
            for guild in self.guilds:
                table_name = str(guild.id)

        except Exception as erro:
            log.error(f"ERROR: {erro}")
            tb = traceback.format_exc()
            log.error(tb)

        log.info(f"Client logged in as {self.user} ID: {self.user.id}")

    async def on_message(self, message: Message, /) -> None:
        channel_trading: int = 1262569655222927371

        if int(message.channel.id) == channel_trading:
            if message.content.startswith("/trad"):
                await self.process_commands(message)

            elif message.author != self.user:
                await asyncio.sleep(0.3)
                await message.delete()
        else:
            if message.content.startswith("/"):
                await self.process_commands(message)

            elif message.content.startswith("l!"):
                await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        await ctx.defer(ephemeral=True)
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('> Comando não encontrado!!', ephemeral=True)
        elif isinstance(error, commands.CommandOnCooldown):
            retry_after = error.retry_after  # Tempo restante em segundos
            tempo_restante = datetime.timedelta(seconds=retry_after)

            dias = tempo_restante.days
            horas, resto_segundos = divmod(tempo_restante.seconds, 3600)
            minutos, segundos = divmod(resto_segundos, 60)

            mensagem = f"> Este comando está em cooldown! Tente novamente em {dias} dias, {horas} horas, {minutos} minutos e {segundos} segundos."
            await ctx.send(mensagem, ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('> Você não tem permissão para usar esse comando! 😪', ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send('> Eu não tenho permissão para executar esse comando! 😪', ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("> Please send all arguments! Type ``/help command`` to view the command details.",
                           ephemeral=True)

        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("> Esse comando não existe! Use ``/help`` para ver a lista completa de comandos.",
                           ephemeral=True)

        elif isinstance(error, commands.MessageNotFound):
            await ctx.send("> Mensagem não encontrada 😪", ephemeral=True)

        elif isinstance(error, commands.CheckFailure):
            await ctx.send("Esse comando está disponível somente para membros verificados!!", ephemeral=True)

        else:
            log_channel = ctx.guild.get_channel(
                data_options["bot_configs"]["channel_bot_erro"])  # Canal de logs de erros

            traceback_message = ''.join(traceback.format_exception(None, error, error.__traceback__))
            await log_channel.send(f'> **Unexpected error:**\n```\n{traceback_message}\n```')


gensen: object = ゲンセン(intents=intents, application_id=data_options["bot_configs"]["client_id"])


async def main():
    async with gensen:
        await gensen.start(DISCORD_TOKEN)


asyncio.run(main())
