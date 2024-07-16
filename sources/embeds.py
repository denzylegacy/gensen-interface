import discord
import random

class CustomEmbed:
	""""
	TODO: Como usar:
	embed = (CustomEmbed("Title", "This is a description")
            .set_author("Author Name", icon_url="http://example.com/icon.png", url="http://example.com/")
            .set_footer("Footer text", icon_url="http://example.com/footer_icon.png")
            .set_thumbnail("http://example.com/thumbnail.png")
            .set_image("http://example.com/image.png")
            .add_field("Field 1", "Field 1 value")
            .add_field("Field 2", "Field 2 value", inline=True)
            .create_embed()
         )
	"""
	def __init__(self, title: str = None, description: str = None, color: discord.Color = None):
		self.title = title
		self.description = description
		self.color = color if color is not None else self.new_color()[0]
		self.fields = []
		self.author = None
		self.footer = None
		self.thumbnail = None
		self.image = None

	def generate_random_color(self):
		# Gera uma lista com três números aleatórios entre 0 e 255
		rgb = [random.randint(0, 255) for _ in range(3)]
		# Concatena os números em uma string no formato RRGGBB
		hex_color = ''.join([hex(n)[2:].zfill(2) for n in rgb])
		# Retorna a cor como um inteiro e como uma string com o prefixo '0x'
		return int(hex_color, 16), f"#{hex_color}"

	def new_color(self):
		color, random_color = self.generate_random_color()
		return color, random_color.replace('#', '0x')
	
	def set_author(self, name: str, icon_url: str = None, url: str = None):
		self.author = {'name': name, 'icon_url': icon_url, 'url': url}
		return self

	def set_footer(self, text: str, icon_url: str = None):
		self.footer = {'text': text, 'icon_url': icon_url}
		return self

	def set_thumbnail(self, url: str):
		self.thumbnail = url
		return self

	def set_image(self, url: str):
		self.image = url
		return self

	def add_field(self, name: str, value: str, inline: bool = False):
		self.fields.append({'name': name, 'value': value, 'inline': inline})
		return self

	def create_embed(self):
		"""
		TODO: 
		- Crie e retorna uma instância de discord.Embed
		"""
		embed = discord.Embed(
			title=self.title, 
			description=self.description, 
			color=16087658  # 16087658, 6912984, 4425552, 13675074
		)

		if self.author:
			embed.set_author(name=self.author['name'], icon_url=self.author['icon_url'], url=self.author['url'])

		if self.footer:
			embed.set_footer(text=self.footer['text'], icon_url=self.footer['icon_url'])

		if self.thumbnail:
			embed.set_thumbnail(url=self.thumbnail)

		if self.image:
			embed.set_image(url=self.image)

		for field in self.fields:
			embed.add_field(name=field['name'], value=field['value'], inline=field['inline'])

		return embed
	