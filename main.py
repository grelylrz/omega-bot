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
    print("Good.")
    with open("config.json", "r") as f:
        data = json.load(f)
    token = data.get("token")
    prefix = data.get("prefix")
    bot = commands.Bot(command_prefix=prefix, intents=intents)
else:
    config_data = {
        "token": "your_token_here",
        "prefix": "!"
    }
    with open('config.json', 'w') as f:
        json.dump(config_data, f, indent=4)
    print("Bad, created.")

def check():
    try:
        response = requests.get("http://121.127.37.17:1212/status")
        #print(f"Response Code: {response.status_code}")  # Выводим код ответа для диагностики

        if response.status_code == 200:
            try:
                data = response.json()  # Пытаемся распарсить JSON
                #print(f"Received Data: {data}")  # Выводим данные для диагностики

                # Обработка данных с дефолтными значениями, если они отсутствуют
                name = data.get("name", "Неизвестное название")
                players = data.get("players", 0)  # По умолчанию 0 игроков
                map_name = data.get("map", "Неизвестная карта")  # Если карта отсутствует, установим "Неизвестная карта"
                round_id = data.get("round_id", "Неизвестный раунд")  # Если id раунда отсутствует
                run_level = data.get("run_level", "Неизвестный уровень")  # Если уровень отсутствует
                preset = data.get("preset", "Неизвестный режим")  # Если режим отсутствует
                round_start_time = data.get("round_start_time", None)
                
                # Если время начала раунда отсутствует, установим значение по умолчанию
                if round_start_time:
                    round_start_time_obj = datetime.fromisoformat(round_start_time.rstrip('Z'))
                else:
                    round_start_time_obj = "Неизвестное время старта"

                return {
                    'name': name,
                    'players': players,
                    'map': map_name,
                    'round_id': round_id,
                    'run_level': run_level,
                    'preset': preset,
                    'round_start_time': round_start_time_obj
                }
            except json.JSONDecodeError as e:
                #print(f"Ошибка при разборе JSON: {e}")
                return False
        else:
            #print(f"Ошибка: сервер вернул код {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return False

@bot.event
async def on_ready():
    print(f'Bot {bot.user} ready!')
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="OmegeDuty, players: not initialized"))

@bot.command()
async def status(ctx):
    status = check()
    if status:
        name = status['name']
        map_name = status['map']
        round_id = status['round_id']
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
        embed.add_field(name="Карта:", value=map_name, inline=True)
        embed.add_field(name="Игроков:", value=players, inline=True)
        embed.add_field(name="Лобби:", value=islobby, inline=True)
        embed.add_field(name="Айди раунда:", value=round_id, inline=True)
        embed.add_field(name="Режим:", value=preset, inline=True)
        embed.add_field(name="Раунд стартовал в:", value=round_start, inline=True)

        await ctx.reply(embed=embed)
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name=f"OmegeDuty, players: {players}"))
    else:
        embed = discord.Embed(
            title="Error.",
            description="beta",
            color=discord.Color.red()
        )
        embed.add_field(name="Ошибка.", value="Ошибка при получении данных (сервер активен?)", inline=True)
        await ctx.reply(embed=embed)

bot.run(token)
