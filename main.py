import os

import discord
import pymysql

from discord import app_commands as commands
from discord.ui import *
from discord.ext.commands import Cog, Bot
from discord.ext import tasks
from dotenv import load_dotenv

from db_tools import DbClient as Database

load_dotenv()


class Corona2(Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents, command_prefix="*")
        self.database = Database(host=os.getenv("MYSQLHOST"),
                                 database=os.getenv("MYSQLDATABASE"),
                                 user=os.getenv("MYSQLUSER"),
                                 password=os.getenv("MYSQLPASSWORD"),
                                 port=int(os.getenv("MYSQLPORT")))

    async def setup_hook(self) -> None:
        await self.add_cog(CoronaCog(self))

    async def on_ready(self):
        await self.tree.sync()
        channel = self.get_channel(774721031147487273)
        views = [await channel.fetch_message(984880252931174500)]
        for view in views:
            self.add_view(RegisterView(self, view))
        print(f"{self.user.name} on the field!")


bot = Corona2()


class CoronaCog(Cog):
    def __init__(self, bot: Corona2):
        self.bot = bot

    @commands.command(name='setup', description="Nie twoja sprawa")
    async def setup_command(self, ctx: discord.Interaction):
        if ctx.user.id != 287258679609393152:
            await ctx.response.send_message("Nie twoja mówiłam", ephemeral=True)
        else:
            embed = discord.Embed.from_dict(
                                    {
                                      "title": "Użytkownicy w grze:",
                                      "description": "<@!355713957656264705>",
                                      "color": 4762980,
                                      "author": {
                                        "name": "Kółeczko Mangowe - zgłoszenia do 13.06.2022",
                                        "icon_url": "https://static.wikia.nocookie.net/yuripedia/images/3/3f/2018-11-19_19-59-36.jpg/revision/latest/scale-to-width-down/270?cb=20200305053754"
                                      }
                                    })
            await ctx.response.send_message("Jeszcze chwila...", embed=embed)
            view = RegisterView(self.bot, await ctx.original_message())
            await ctx.edit_original_message(content=None, view=view)

    @tasks.loop(seconds=60)
    async def roll_out(self, ctx: discord.Interaction):
        users =


class Questionary(Modal):
    name = TextInput(label="Nazwa użytkownika MAL (może być puste):", custom_id="circle_mal_id_d", style=discord.TextStyle.short, required=False)
    address = TextInput(label="Adres wysyłki lub preferowany paczkomat:", style=discord.TextStyle.paragraph)
    phone = TextInput(label="(Dla paczkomatu) Telefon:", style=discord.TextStyle.short, required=False)

    def __init__(self, bot, message):
        self.bot: Corona2 = bot
        self.message: discord.Message = message
        super().__init__(title="Rejestracja do Mangowego Kółeczka",
                         custom_id="circle_questionary_d")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Jesteś w grze!", ephemeral=True)
        try:
            self.bot.database.create_user(interaction.user.id, self.address.value, self.phone.value)
        except pymysql.IntegrityError:
            pass
        if self.name:
            try:
                self.bot.database.connect_users_mal_account(self.name.value, interaction.user.id)
            except pymysql.IntegrityError:
                pass
        embed = self.message.embeds[0]
        embed.description = embed.description + f"\n<@!{interaction.user.id}>"
        await self.message.edit(embed=embed)

    def on_timeout(self) -> None:
        pass


class RegisterButton(Button):
    def __init__(self, bot, message):
        self.bot: Corona2 = bot
        self.message = message
        super().__init__(style=discord.ButtonStyle.green, label="Zarejestruj", custom_id="circle_register_d")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(Questionary(self.bot, self.message))


class RegisterView(View):
    def __init__(self, bot, message):
        super().__init__(timeout=None)
        self.add_item(RegisterButton(bot, message))

bot.run(os.getenv('TOKEN'))