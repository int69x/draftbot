import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")  # Assure-toi que la variable d’environnement est bien définie

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # Pour slash commands

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
@bot.event
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"🔁 {len(synced)} commande(s) slash synchronisées.")
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation des commandes : {e}")


from discord.ext import commands
from discord import app_commands
import os
import re
import httpx

TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ➤ Fonction pour extraire les pseudos de l’URL OP.GG
def extract_summoners(opgg_url: str):
    match = re.search(r"multisearch/\w+\?(.*)", opgg_url)
    if not match:
        return []
    query_string = match.group(1)
    raw_names = [pair.split('=')[1] for pair in query_string.split('&') if '=' in pair]
    names = [name.replace('%20', ' ') for name in raw_names]
    return names

# ➤ Appelle l'API DPM.lol
async def fetch_dpm_data(summoner: str):
    try:
        name_slug = summoner.replace(" ", "-").lower()
        url = f"https://dpm.lol/api/player/{name_slug}"
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            if res.status_code == 200:
                return res.json()
            else:
                return None
    except Exception:
        return None

# ➤ Slash command : /scout
@tree.command(name="scout", description="Analyse IA de l'équipe adverse via DPM.lol")
@app_commands.describe(url="Lien OP.GG multi-search (euw)")
async def scout(interaction: discord.Interaction, url: str):
    await interaction.response.defer(thinking=True)

    summoners = extract_summoners(url)
    if not summoners:
        await interaction.followup.send("❌ Aucun invocateur trouvé dans l'URL OP.GG.")
        return

    report = f"🔍 **Analyse IA via DPM.lol en cours...**\n\n"
    recommended_bans = []

    for name in summoners:
        data = await fetch_dpm_data(name)
        if not data:
            report += f"⚠️ `{name}` non trouvé sur DPM.lol\n"
            continue

        report += f"👤 **{data['name']}** ({data.get('role', 'inconnu')})\n"

        champs = data.get("champions", [])[:3]
        for champ in champs:
            champ_name = champ.get("name", "??")
            winrate = champ.get("winrate", 0)
            games = champ.get("games", 0)
            report += f"• {champ_name} – {winrate}% WR – {games} parties\n"

            if winrate >= 55 and games >= 10:
                recommended_bans.append(f"{champ_name} (joué par {data['name']})")

        report += "\n"

    if recommended_bans:
        report += f"🚫 **Bans recommandés par l'IA :**\n"
        for ban in recommended_bans:
            report += f"• {ban}\n"
    else:
        report += "✅ Aucun pick prioritaire détecté."

    await interaction.followup.send(report[:2000])  # limite Discord

    except Exception as e:
        print(f"❌ Erreur de sync : {e}")

# La commande /scout
@tree.command(name="scout", description="Analyse IA via OP.GG")
@app_commands.describe(url="Lien OP.GG de l'équipe adverse")
async def scout(interaction: discord.Interaction, url: str):
    await interaction.response.defer()  # Affiche "thinking..." sur Discord
    # Simule l'analyse IA (à remplacer par appel réel à DPM ou autre)
    result = f"🔍 Analyse IA en cours pour : {url}\n🎯 **Scouting IA terminé :**\n\n"
    result += f"⚠️ Aucun joueur trouvé (fonction à compléter)"
    await interaction.followup.send(result)

bot.run(TOKEN)
