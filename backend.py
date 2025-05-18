import configparser
import discord

parser = configparser.ConfigParser()
parser.read("Config.ini", encoding="utf-8")


def get_roles_club(roles, NAME_CLUB):
    with open(NAME_CLUB, "r", encoding="utf-8") as f:
        for ligne in f:
            print(ligne.strip())  # .strip() pour enlever le saut de ligne

def est_prefixe(nom, prefixe):
    """Renvoie True si 'nom' commence par 'prefixe'."""
    return nom.lower().startswith(prefixe.lower())


import configparser

def get_config(path, section, parameter):
    # Crée un parser et lit le fichier .ini
    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")

    # Vérifie si la section et le paramètre existent
    if section not in parser or parameter not in parser[section]:
        raise ValueError(f"'{parameter}' introuvable dans la section [{section}]")

    # Récupère la valeur brute (ex: "123" ou "id1, id2")
    raw_value = parser[section][parameter].strip()

    # Si plusieurs valeurs séparées par des virgules
    if "," in raw_value:
        valeurs = [item.strip() for item in raw_value.split(",")]

        # Convertit chaque élément en int si possible, sinon laisse en str
        resultats = []
        for val in valeurs:
            if val.isdigit():
                resultats.append(int(val))
            else:
                resultats.append(val)
        return resultats

    # Si une seule valeur
    else:
        return raw_value


def get_AdminRolesID(path):
    roles_admin = get_config(path, "roles", "role_admin")

    roles_admin_id = []
    for role in roles_admin :
        role_admin_id = get_config(path, "roles", role)
        roles_admin_id.append(role_admin_id)
    return roles_admin_id


def have_AdminRoles(ConfigPath, Roles):
    roles_admin_id = get_AdminRolesID(ConfigPath)
    roles_admin_id = [int(role_id) for role_id in roles_admin_id]

    if not any(role.id in roles_admin_id for role in Roles):
        return False
    return True

async def create_clubRole(guild, ClubName, ConfigPath):
    role_prefixes = get_config(ConfigPath, "roles", "role_prefix")
    created_roles = {}  # stocke

    for prefix in role_prefixes: # Crée un rôle pour chaque préfixe
        role_name = f"{prefix} {ClubName}"
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            role = await guild.create_role(name=role_name, mentionable=True)
        created_roles[prefix] = role

    return created_roles


async def create_clubCategory(guild, ClubName, created_roles):
    overwrites_cat = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False)
    }
    for role in created_roles.values():
        overwrites_cat[role] = discord.PermissionOverwrite(view_channel=True)

    # Créer la catégorie
    category = await guild.create_category(name=f"[{ClubName}]", overwrites=overwrites_cat)

    # Salon texte général pour tous les rôles du club
    await guild.create_text_channel(f"general", category=category)
    await guild.create_voice_channel(f"discussion", category=category)

    # Salon vocal staff : Staff, Tréso, Président.e
    overwrites_staff = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        created_roles["Staff"]: discord.PermissionOverwrite(view_channel=True, connect=True),
        created_roles["Tréso"]: discord.PermissionOverwrite(view_channel=True, connect=True),
        created_roles["Président.e"]: discord.PermissionOverwrite(view_channel=True, connect=True)
    }
    await guild.create_text_channel(f"staff", category=category, overwrites=overwrites_staff)

    # Salon vocal bureau : Tréso, Président.e uniquement
    overwrites_bureau = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        created_roles["Tréso"]: discord.PermissionOverwrite(view_channel=True, connect=True),
        created_roles["Président.e"]: discord.PermissionOverwrite(view_channel=True, connect=True)
    }
    await guild.create_text_channel(f"restreint", category=category, overwrites=overwrites_bureau)

    return category

def has_president_or_treso_role(member, guild, club_name):
    club_keywords = club_name.lower().split()

    for role in member.roles:
        role_name_lower = role.name.lower()
        # Vérifie présence de "président" ou "tréso" dans le nom du rôle
        if "président.e" in role_name_lower or "tréso" in role_name_lower :
            # Vérifie que tous les mots du club sont contenus dans le nom du rôle
            if all(keyword in role_name_lower for keyword in club_keywords):
                return True
    return False