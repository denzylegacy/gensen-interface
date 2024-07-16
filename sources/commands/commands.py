import traceback
import discord
import typing
from discord.ext import commands
from typing import Optional, Literal
from discord import app_commands

from local_io import JSONHandler
from sources.decorators import is_bot_owner
import secrets, string


data_options = JSONHandler(file_path="./infra/options.json").read_json()

MY_GUILD_ID = discord.Object(data_options["bot_configs"]["sync_guild_id"], type=discord.Guild)


class Commands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	### command 1
	@commands.has_permissions(administrator=True)
	@commands.hybrid_command(name='sync', brief="sincronizar comandos")
	@commands.cooldown(1, 10, commands.BucketType.user)
	@is_bot_owner
	@app_commands.guilds(MY_GUILD_ID)
	async def sync_command(
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

	### command 2
	@commands.has_permissions(administrator=True)
	@commands.hybrid_command(name='del_key_redis', brief="Deletar uma chave do servidor Redis")
	@commands.cooldown(1, 30, commands.BucketType.user)
	@is_bot_owner
	@app_commands.guilds(MY_GUILD_ID)
	async def del_key_redis_command(self, ctx, key: str):
		await ctx.defer(ephemeral=True)
		await self.bot.redis.delete(key)
		await ctx.send(f"> A chave {key} foi deletada com sucesso! ✅")

	### command 3
	@commands.has_permissions(administrator=True)
	@commands.hybrid_command(name='clear_all_redis', brief="Apaga o banco de dados atual do servidor Redis")
	@commands.cooldown(1, 30, commands.BucketType.user)
	@is_bot_owner
	@app_commands.guilds(MY_GUILD_ID)
	async def clear_all_redis_command(self, ctx):
		await ctx.defer(ephemeral=True)
		await self.bot.redis.flushdb()  # apaga o banco de dados atual ou self.bot.redis.flushall() para pagar todos
		await ctx.send(f"> O banco de dados foi resetado! ✅")

	# COMANDOS DE PAGAMENTO E BANCO DE DADOS MYSQL
	### command 5
	@commands.has_permissions(administrator=True)
	@commands.hybrid_command(name='verificar_pagamento')
	@commands.cooldown(1, 30, commands.BucketType.user)
	@is_bot_owner
	@discord.app_commands.describe(ordem_id="Ordem do pagamento")
	@app_commands.guilds(MY_GUILD_ID)
	async def verificar_pagamento_command(self, ctx, ordem_id: str):
		"""Verificar o estado de uma transação usando a ordem de pagamento"""
		await ctx.defer(ephemeral=True)

		payment_status = await self.bot.PAYPAL.check_payment_status(ordem_id)

		if payment_status:
			msg = data_options["payments_messages"]["order_status_success"]
			await ctx.send(
				content=f'{msg} ✅'.format(ordem_id)
			)
		else:
			msg = data_options["payments_messages"]["order_status_error"]
			await ctx.send(
				content=f'{msg} ❌'.format(ordem_id)
			)

	### command 7
	@commands.has_permissions(administrator=True)
	@is_bot_owner
	@commands.hybrid_command(name='deletar_todas_tabelas_pagamentos')
	@commands.cooldown(1, 30, commands.BucketType.user)
	@app_commands.guilds(MY_GUILD_ID)
	async def deletar_todas_tabelas_pagamentos_command(self, ctx):
		"""Deletar a tabela de pagamentos!"""
		await ctx.defer(ephemeral=True)
		guild_id = ctx.guild_id
		self.bot.MYSQL.delete_payments_table(table_name=str(guild_id))

		msg = data_options["mysql_messages"]["delete_table_success"]
		await ctx.send(
			f'{msg} ✅'.format(guild_id)
		)

	### command 8
	@commands.has_permissions(administrator=True)
	@is_bot_owner
	@commands.hybrid_command(name='resetar_tabelas_pagamentos')
	@commands.cooldown(1, 30, commands.BucketType.user)
	@app_commands.guilds(MY_GUILD_ID)
	async def resetar_tabelas_pagamentos_payments_command(self, ctx):
		"""Limpar a tabela de pagamentos pendentes"""
		await ctx.defer(ephemeral=True)
		guild_id = ctx.guild_id
		self.bot.MYSQL.clear_payments_table(table_name=str(guild_id))

		msg = data_options["mysql_messages"]["clear_table_payments"]
		await ctx.send(
			content=f'{msg}'.format(guild_id)
		)

	### command 8
	@commands.has_permissions(administrator=True)
	@is_bot_owner
	@commands.hybrid_command(name='configurar_idioma')
	@commands.cooldown(1, 30, commands.BucketType.user)
	@app_commands.guilds(MY_GUILD_ID)
	async def configurar_idioma_command(self, ctx, language: typing.Literal['Português', 'English']):
		"""Definir o idioma do bot"""
		await ctx.defer(ephemeral=True, thinking=True)
		if language == "Português":
			language_ = "pt-br"
		elif language == "English":
			language_ = "en-us"
		else:
			language_ = "pt-br"

		guild_id = ctx.guild_id
		table_name = 'lan' + str(guild_id)

		msg = data_options["bot_configs"]["set_language"]
		await ctx.send(
			f'{msg}'.format(language)
		)

	# command 10
	@commands.hybrid_command(name="criar_convite", brief="Criar Convite")
	@commands.has_permissions(administrator=True)
	@commands.cooldown(1, 30, commands.BucketType.user)
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

	# command 11
	@commands.hybrid_command(name="gerar_token", brief="Gerar Token")
	@commands.has_permissions(administrator=True)
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def create_invite(
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
	await bot.add_cog(Commands(bot), guild=MY_GUILD_ID)
