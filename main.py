import datetime
import os

import discord
import pymysql

from discord import app_commands as commands
from discord.ui import *
from discord.ext.commands import Cog, Bot
from discord.ext import tasks
from dotenv import load_dotenv

import db_tools
from db_tools import DbClient as Database
import inpost_checker

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
        # self.roll_out.start()

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

    @commands.command(name='sent', description='Indicate sending package')
    @commands.describe(inpost_number="Numer śledzenia przesyłki inpost", manga_title='Tytuł zamówionej mangi')
    async def package_sent(self, ctx: discord.Interaction, inpost_number: str, manga_title: str):
        await ctx.response.send_message("<a:1656_idle:822853958963953696> Sprawdzam...")
        try:
            state = inpost_checker.get_package_state(int(inpost_number))
        except ValueError:
            await ctx.followup.send(content="<:Denied:821395055217475615> Niepoprawny numer paczki")
        else:
            pair = self.bot.database.get_pair(ctx.user.id)
            pair.inpost, pair.manga_title = int(inpost_number), manga_title
            self.bot.database.update_pair(pair)
            await ctx.followup.send(content=f"<:Approved:821395055515664465> Paczka została przyjęta\nAktualny status paczki: {state.value}")


    # @tasks.loop(hours=1)
    # async def roll_out(self):
    #     await bot.wait_until_ready()
    #     users = self.bot.database.get_randomly_ordered_users()
    #     for i in range(len(users)):
    #         sender = users[i][0]
    #         receiver = users[i - 1][0]
    #         if sender == 355713957656264705:
    #             sender = 287258679609393152
    #         sender_user = bot.get_user(users[i][0])
    #         embed = discord.Embed.from_dict({"title": "Dane adresata","description": f"*Do:* <@!{receiver}>; *Od:* <@!{sender}>\n**Poniższe dane są poufne, nie pokazuj ich nikomu!**\n*Paczkomat:*\n||{users[i - 1][2]}||\n*Numer Telefonu:*\n||{users[i - 1][3]}||","color": 2467904,"fields": [{"name": "Gdzie kupić fizycznie?","value": "**Yatta** - Kiełbaśnicza 25, 50-110 Wrocław\n**Empik** - Praktycznie kurwa wszędzie","inline": True},{"name": "Gdzie kupić online?","value": "U pośrednika:\n[Empik](https://www.empik.com/)\n[Yatta](https://yatta.pl)\nU wydawnictw:\n[Waneko](https://sklepwaneko.pl/)\n[J.P.Fantastica](https://www.jpf.com.pl/)\n[Studio JG](https://studiojg.pl/)","inline": True},{"name":"Co dalej?","value": "Po zamówieniu mangi wywołaj tu komendę\n`/sent <tytuł> <nr przesyłki inpost>`\nGdy wszystkie przesyłki dotrą do nadawców lista tytułów zostanie opublikowana na <#774721031147487273>"}],"author":{"name": "Kółeczko Mangowe - informacja zwrotna","icon_url": "https://images-ext-2.discordapp.net/external/1sIwsLTPCXHcleyf112KDe5gSLpzpmGDDNZ1753v8Bc/%3Fcb%3D20200305053754/https/static.wikia.nocookie.net/yuripedia/images/3/3f/2018-11-19_19-59-36.jpg/revision/latest/scale-to-width-down/270"}})
    #         await sender_user.send(embed=embed)
    #         print(f"{sender} sending to {receiver}")
    #
    # @roll_out.before_loop
    # async def before_roll_out(self):
    #     await bot.wait_until_ready()

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