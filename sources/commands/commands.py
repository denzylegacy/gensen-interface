import traceback
import discord
import typing
from discord.ext import commands
from typing import Optional, Literal
from discord import app_commands

from local_io import JSONHandler
from sources.decorators import bot_owner
import secrets, string


data_options = JSONHandler(file_path="./infra/options.json").read_json()

MY_GUILD_ID = discord.Object(data_options["bot_configs"]["sync_guild_id"], type=discord.Guild)


class GeneralCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	### command 1
	@commands.hybrid_command(name="sync", brief="Sync commands")
	@commands.cooldown(1, 10, commands.BucketType.user)
	@app_commands.guilds(MY_GUILD_ID)
	@commands.has_permissions(administrator=True)
	@bot_owner
	async def sync(
			self,
			ctx: commands.Context,
			guilds: Optional[str] = None,
			spec: Optional[Literal[
				"Clear and local sync",
				"Clear local slash",
				"Clear local message context",
				"Clear local user context",
				"Clear global slash",
				"Clear global message context",
				"Clear global user context",
				"Global sync",
				"Copy global to local",
				"Local sync"
			]
			] = None
	) -> None:
		await ctx.defer(ephemeral=True)
		try:
			msg = await ctx.send("Wait!")

			##Guilds
			try:
				next_word = guilds.split(';', maxsplit=1)[-1].split(maxsplit=1)[0]
				next_word = next_word.replace(" ", "")

				if (next_word != guilds) and (';' not in guilds):
					msg1 = data_options["general_cmd"]["sync_error_semicolon"]
					await msg.edit(content=f'> *{msg1}* 😪')
					return

				guilds = guilds.replace(" ", "").split(';')

				guilds = (discord.Object(id) for id in guilds)
			except:
				guilds = None
			# End guilds

			if guilds is None:
				guilds = ctx.guild
				if spec is not None:
					if spec.lower() == "clear and local sync":
						self.bot.tree.clear_commands(guild=guilds)
						await self.bot.tree.sync(guild=guilds)
					elif spec.lower() == "local sync":
						await self.bot.tree.sync(guild=guilds)
					elif spec.lower() == "copy global to local":
						self.bot.tree.copy_global_to(guild=guilds)
						await self.bot.tree.sync(guild=guilds)
					elif spec.lower() == "clear local slash":
						self.bot.tree.clear_commands(guild=guilds, type=discord.AppCommandType.chat_input)
						await self.bot.tree.sync(guild=guilds)
					elif spec.lower() == "clear local message context":
						self.bot.tree.clear_commands(guild=guilds, type=discord.AppCommandType.message)
						await self.bot.tree.sync(guild=guilds)
					elif spec.lower() == "clear local user context":
						self.bot.tree.clear_commands(guild=guilds, type=discord.AppCommandType.user)
						await self.bot.tree.sync(guild=guilds)
					elif spec.lower() == "clear global slash":
						self.bot.tree.clear_commands(guild=None, type=discord.AppCommandType.chat_input)
						await self.bot.tree.sync()
					elif spec.lower() == "clear global message context":
						self.bot.tree.clear_commands(guild=None, type=discord.AppCommandType.message)
						await self.bot.tree.sync()
					elif spec.lower() == "clear global user context":
						self.bot.tree.clear_commands(guild=None, type=discord.AppCommandType.user)
						await self.bot.tree.sync()
					elif spec.lower() == "global sync":
						await self.bot.tree.sync()

					await msg.edit(
						content=f"Synced command(s) {spec.lower()}! ✅"
					)
					return

			fmt = 0
			for guild in guilds:
				try:
					await self.bot.tree.sync(guild=guild)
				except discord.HTTPException:
					pass
				else:
					fmt += 1

			await msg.edit(content=f"Synced the tree to guild{'s'[:fmt ^ 1]}! ✅")
		except Exception as e:
			print(f"An error occurred: {e}")
			tb = traceback.format_exc()
			print(tb)

	# command 2
	@commands.hybrid_command(name="create_invite", brief="Create Invitation")
	@commands.cooldown(1, 30, commands.BucketType.user)
	@commands.has_permissions(administrator=True)
	async def create_invite(
			self, ctx, reason=None, max_age=0, max_uses=0, temporary=False,
		unique=True, target_type=None, target_user=None, target_application_id=None
	):
		"""Cria um convite"""
		await ctx.defer(ephemeral=True)

		invite = await ctx.channel.create_invite(
			reason=reason, max_age=max_age, max_uses=max_uses, temporary=temporary,
			unique=unique, target_type=target_type, target_user=target_user,
			target_application_id=target_application_id
		)
		await ctx.send(
			f"🔗 Link para este canal: {invite.url}"
		)

	# command 3
	@commands.hybrid_command(name="gerar_token", brief="Gerar Token")
	@commands.cooldown(1, 30, commands.BucketType.user)
	@commands.has_permissions(administrator=True)
	async def gerar_token(
			self, ctx, characters=50, case_sensitivity=False, upper_case=False
	):
		"""Gerador de Tokens"""
		await ctx.defer(ephemeral=True)

		def generate_token(length, cs, uc):
			secret = "".join(
				secrets.choice(string.ascii_letters + string.digits) for _ in range(length)
			)
			if cs:
				return secret
			elif uc:
				return secret.upper()
			else:
				return secret.lower()

		token = generate_token(characters, case_sensitivity, upper_case)

		await ctx.send(
			f"📦 Seu token de {len(token)} caracteres:\n||{token}||"
		)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(GeneralCommands(bot), guild=MY_GUILD_ID)
