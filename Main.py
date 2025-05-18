from discord import app_commands
from discord.ext import commands
from backend import *

ConfigPath = "Config.ini"
Token = get_config(ConfigPath, "bot", "token")

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix=get_config(ConfigPath, "bot", "prefix"), intents=intents)

print(get_config(ConfigPath, "bot", "prefix"))

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot connecté en tant que {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong !")

@bot.command()
async def newClub(ctx, *, ClubName=None):
    auteur = ctx.author

    if ClubName is None:
        await ctx.send("⛔ Utilisation : `!newclub <NomDuClub>`")
        return

    if not have_AdminRoles(ConfigPath, auteur.roles):
        await ctx.send("⛔ Tu n'as pas les permissions pour faire ça.")
        return

    guild = ctx.guild
    created_roles = await create_clubRole(guild, ClubName, ConfigPath)
    await create_clubCategory(guild, ClubName, created_roles)
    await ctx.send(f"✅ Club `{ClubName}` créé avec succès !")

@bot.command()
async def giveRole(ctx, member: discord.Member, *, args):

    parts = args.split()
    if len(parts) < 2:
        await ctx.send("❌ Usage : !giverole @membre <NomDuClub> <PrefixDuRôle>")
        return

    prefix = parts[-1]               # dernier mot -> préfixe
    club_name = " ".join(parts[:-1])  # tout sauf le dernier -> nom du club

    auteur = ctx.author

    # Vérif roles admin ou président/tréso du club
    if not (has_president_or_treso_role(auteur, ctx.guild, club_name) or have_AdminRoles(ConfigPath, auteur.roles)):
        await ctx.send("⛔ Tu n'as pas les permissions pour faire ça.")
        return

    role_name = f"{prefix} {club_name}"  # Exemple: "staff club welcome"

    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        await ctx.send(f"❌ Le rôle `{role_name}` n'existe pas.")
        return

    try:
        await member.add_roles(role)
        await ctx.send(f"✅ Le rôle `{role.name}` a été ajouté à {member.mention}.")
    except discord.Forbidden:
        await ctx.send("⛔ Je n'ai pas la permission d'ajouter ce rôle.")
    except Exception as e:
        await ctx.send(f"⚠️ Une erreur est survenue : {e}")


@bot.tree.command(name="updateclub", description="Associe un président et un trésorier à un club.")
@app_commands.describe(
    club_name="Nom du club",
    president="Mention du président",
    treso="Mention du trésorier"
)
async def updateclub(interaction: discord.Interaction, club_name: str, president: discord.Member, treso: discord.Member):
    autorRoles = interaction.user.roles

    if not have_AdminRoles(ConfigPath, autorRoles):
        await interaction.response.send_message("⛔ Tu n'as pas les permissions pour faire ça.")
        return

    Prole = discord.utils.get(interaction.guild.roles, name=f"Président.e {club_name}")
    Trole = discord.utils.get(interaction.guild.roles, name=f"Tréso {club_name}")

    if Prole is None or Trole is None:
        await interaction.response.send_message(f"❌ Le club `{club_name}` n'existe pas.")
        return

    try:
        await president.add_roles(Prole)
        await treso.add_roles(Trole)
        await interaction.response.send_message(f"📌 Mise à jour du club `{club_name}` :\n👤 Président.e : {president.mention}\n💰 Tréso : {treso.mention}")
    except discord.Forbidden:
        await interaction.response.send_message("⛔ Je n'ai pas la permission d'ajouter ces rôles.")
        return
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Une erreur est survenue : {e}")
        return

bot.run(Token)
