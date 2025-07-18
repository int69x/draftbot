import os
import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

ROLE_ORDER = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
ROLE_MAP = {
    "TOP": "Top",
    "JUNGLE": "Jungle",
    "MIDDLE": "Mid",
    "BOTTOM": "ADC",
    "UTILITY": "Support"
}


def fetch_dpm_data(profile_name):
    url = f"https://dpm.lol/{profile_name}"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    players = []

    for section in soup.select("div.player"):
        try:
            name = section.select_one("div.summoner-name").text.strip()
            role_raw = section.select_one("div.role").text.strip().upper()
            role = ROLE_MAP.get(role_raw, role_raw)

            champions = []
            rows = section.select("table.champion-stats tbody tr")
            for row in rows[:3]:
                cols = row.find_all("td")
                champ_name = cols[0].text.strip()
                winrate = cols[1].text.strip()
                games = cols[2].text.strip()
                champions.append({
                    "name": champ_name,
                    "winrate": winrate,
                    "games": games
                })

            players.append({
                "name": name,
                "role": role,
                "champions": champions
            })
        except:
            continue

    return players


def generate_ban_recommendations(players):
    bans = []
    for role in ["Top", "Jungle", "Mid", "ADC", "Support"]:
        role_champs = []
        for player in players:
            if player["role"] == role and player["champions"]:
                for champ in player["champions"]:
                    try:
                        win = int(champ["winrate"].replace('%', ''))
                        games = int(champ["games"])
                        if games >= 5 and win >= 55:
                            role_champs.append((champ["name"], win, games, player["name"]))
                    except:
                        continue
        if role_champs:
            best = sorted(role_champs, key=lambda x: (-x[1], -x[2]))[0]
            bans.append({
                "champion": best[0],
                "winrate": best[1],
                "games": best[2],
                "player": best[3],
                "role": role
            })
    return bans


@bot.command()
async def scout(ctx, *, profile_name):
    await ctx.send("🔍 Analyse IA en cours via DPM.lol...")

    data = fetch_dpm_data(profile_name)
    if not data:
        await ctx.send("❌ Impossible de récupérer les données. Vérifie le lien DPM.")
        return

    report = "🎯 **Scouting IA terminé :**\n\n"
    for player in data:
        report += f"👤 **{player['name']}** ({player['role']})\n"
        for champ in player['champions']:
            report += f"• {champ['name']} – {champ['winrate']} ({champ['games']} games)\n"
        report += "\n"

    bans = generate_ban_recommendations(data)
    if bans:
        report += "📛 **Bans recommandés IA :**\n"
        for b in bans:
            report += f"🔒 {b['champion']} ({b['role']}) – {b['winrate']}% ({b['games']} games) – cible : {b['player']}\n"
    else:
        report += "✅ Aucun ban critique détecté."

    await ctx.send(report)


bot.run(os.getenv("TOKEN"))

