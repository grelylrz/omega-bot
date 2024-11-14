import os
import json
import requests
from datetime import datetime
import discord
from discord.ext import commands

token = None
prefix = None
intents = discord.Intents.default()
intents.message_content = True

print("File...")
if os.path.isfile("config.json"):
    global token
    global prefix
    print("Good.")
    data = json.load(file)
    token = data.get("token")
    prefix = data.get("prefix")
    bot = commands.Bot(command_prefix=prefix, intents=intents)
else:
    config_data = {
        "token": "your_token_here",
        "prefix": "!"
    }
    with open('config.json', 'w') as file:
        json.dump(config_data, file, indent=4)
    print("Bad,created.")
import requests
from datetime import datetime

def check():
    response = requests.get("http://121.127.37.17:1212/status")
    if response.status_code == 200:
        data = response.json()
        name = data.get("name")
        players = data.get("players")
        map_name = data.get("map")
        round_id = data.get("round_id")
        run_level = data.get("run_level")
        preset = data.get("preset")
        round_start_time = data.get("round_start_time")
        round_start_time_obj = datetime.fromisoformat(round_start_time.rstrip('Z'))
        return {
            'name': name,
            'players': players,
            'map': map_name,
            'round_id': round_id,
            'run_level': run_level,
            'preset': preset,
            'round_start_time': round_start_time_obj
        }
    else:
        return False
@bot.event
async def on_ready():
    print(f'Bot {bot.user} ready!')
@bot.command()
async def status(ctx):
  status = check()
  if status:
    name = status['name']
    map = status['map']
    round = status['round_id']
    islobby = status['run_level']
    preset = status['preset']
    round_start = status['round_start_time']
    players = status['players']
    embed = discord.Embed(
        title="Статус",
        description="beta",
        color=discord.Color.green()
    )
    embed.add_field(name="Название:", value=name, inline=True)
    embed.add_field(name="Карта:", value=map, inline=True)
    embed.add_field(name="Игроков:", value=players, inline=True)
    embed.add_field(name="Лобби:", value=islobby, inline=True)
    embed.add_field(name="Айди раунда:", value=round, inline=True)
    embed.add_field(name="Режим:", value=preset, inline=True)
    embed.add_field(name="Раунд стартовал в:", value=round_start, inline=True)
    await ctx.send(embed=embed)
  else:
    embed = discord.Embed(
        title="Error.",
        description="beta",
        color=discord.Color.red()
    )
    embed.add_field(name="Ошибка.", value="Ошибка при получении данных(сервер активен?)", inline=True)
    await ctx.send(embed=embed)
bot.run(token)
