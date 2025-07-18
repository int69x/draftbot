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
    try:
        synced = await tree.sync()
        print(f"🔁 {len(synced)} commande(s) slash synchronisées.")
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
