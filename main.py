import os
import json
import requests
from datetime import datetime
import discord
from discord.ext import commands
import psutil
import aiohttp
import yandex_music

token = None
prefix = None
iptoken = None
admin_role = None
watchdog_role = None
music_token = None
runned_cmds = 0
intents = discord.Intents.default()
intents.message_content = True
start_time = None
TARGET_USER_ID = 1284441087745851474
server_dir = "/space-station-14/bin/Content.Server/"
server_run = "./space-station-14/bin/Content.Server/Content.Server"

print("File...")
if os.path.isfile("config.json"):
    print("Good.")
    with open("config.json", "r") as f:
        data = json.load(f)
    token = data.get("token")
    prefix = data.get("prefix")
    iptoken = data.get("iptoken")
    admin_role = int(data.get("admin_id"))
    music_token = data.get("music_token")
    watchdog_role = int(data.get("watchdog_role"))
    bot = commands.Bot(command_prefix=prefix, intents=intents)
    yandex_client = yandex_music.Client(music_token).init()
else:
    config_data = {
        "token": "your_token_here",
        "prefix": "!",
        "iptoken": "ip_info_token_here",
        "admin_id": "id_here",
        "watchdog_role": "your shiza's role here",
        "music_token": "your yandex music token here"
    }
    with open('config.json', 'w') as f:
        json.dump(config_data, f, indent=4)
    print("Bad, created.")
async def get_ip_info(ip):
    url = f"https://ipinfo.io/{ip}?token={iptoken}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                country = data.get('country', 'IDK')
                timezone = data.get('timezone', 'IDK')
                return country, timezone
            else:
                return None, None
def check():
    try:
        response = requests.get("http://121.127.37.17:1212/status")
        #print(f"Response Code: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                #print(f"Received Data: {data}")
                name = data.get("name", "idk")
                players = data.get("players", 0)
                map_name = data.get("map", "idk")
                round_id = data.get("round_id", "idk")
                run_level = data.get("run_level", "idk")
                preset = data.get("preset", "idk")
                round_start_time = data.get("round_start_time", None)
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
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Да."))
    global start_time
    start_time = datetime.now()
    #print(sum(guild.member_count for guild in bot.guilds))
@bot.event
async def on_command(ctx):
    global runned_cmds
    runned_cmds+= 1
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
        if islobby == 1:
            islobby = "Нет."
        elif islobby == 0:
            islobby = "Да."
        elif islobby == 2:
            islobby = "Пре-раунд."
        else:
            islobby = islobby + " бот не смог определить,я трещу!"
        embed = discord.Embed(
            title="Статус",
            description="Время не по мск.",
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
    else:
        embed = discord.Embed(
            title="Error.",
            description="beta",
            color=discord.Color.red()
        )
        embed.add_field(name="Ошибка.", value="Ошибка при получении данных (сервер активен?)", inline=True)
        await ctx.reply(embed=embed)
@bot.command()
async def stats(ctx):
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total / 1024 / 1024
    used_memory = memory_info.used / 1024 / 1024
    current_time = datetime.now()
    uptime_duration = current_time - start_time
    hours, remainder = divmod(int(uptime_duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    unique_userz = sum(guild.member_count for guild in bot.guilds)
    await ctx.send(f"Бот работает: {hours}h {minutes}mins {seconds}sec\nЗапущено команд: {runned_cmds}\nУникальных юзеров: {unique_userz}\nCPU: {cpu_percent:.2f}%\nRAM: {used_memory:.2f}/{total_memory:.2f} MB")
@bot.command()
async def ip(ctx, ip: str):
    if discord.utils.get(ctx.author.roles, id=admin_role):
        country, timezone = await get_ip_info(ip)
        if country and timezone:
            await ctx.reply(f"{country}\n{timezone}")
        else:
            await ctx.reply(f"Не удалось получить информацию для IP.")
    else:
        await ctx.send("У вас нет доступа.")
#@bot.command()
#async def ip(ctx, ip: str):
#    if discord.utils.get(ctx.author.roles, id=watchdog_role):
#        cur_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#        os.system(f"mkdir build{cur_time}")
#        os.system(f"cd build{cur_time}")
#        os.system("git clone https://github.com/grelylrz/space-station-14-2")
#        os.system("cd space-station-14-2")
#        os.system(f"python ./RUN_THIS.py")
#        os.system(f"git submodule update --init --recursive")
#        os.system(f"dotnet build --configuration Release")
#    else:
#        await ctx.send("У вас нет доступа.")
#@bot.command()
#async def start(ctx):
#    global server_process
#    if server_process and server_process.poll() is None:
#        await ctx.send("Сервер уже запущен, вы глупи?")
#        return
#    try:
#        server_process = subprocess.Popen(
#            server_run.split(),
#            cwd=server_dir,
#            stdout=subprocess.PIPE,
#            stderr=subprocess.PIPE
#        )
#        await ctx.send("Запускаю!")
#    except Exception as e:
#        await ctx.send(f"Я ТРЕЩУ ПО ШВАМ!")
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Я отключился от голосового канала!")
    else:
        await ctx.send("Я не нахожусь в голосовом канале!")

@bot.command()
async def play(ctx, *, track_name: str):
    if not ctx.author.voice:
        await ctx.send("Вы должны быть в голосовом канале!")
        return

    if not ctx.voice_client:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Подключился: {channel.name}")

    try:
        search_result = yandex_client.search(track_name)
        tracks = search_result.tracks.results
        if not tracks:
            await ctx.send(f"'{track_name}' не нашелся.")
            return
        track = tracks[0]
        filename = f"{track.id}.mp3"
        await ctx.send(f"Нашёл: {track.title} — {', '.join(artist.name for artist in track.artists)}")
        track.download(filename, codec='mp3', bitrate_in_kbps=192)
        ctx.voice_client.stop()
        ffmpeg_options = {'options': '-vn'}
        source = discord.FFmpegPCMAudio(filename, **ffmpeg_options)
        ctx.voice_client.play(source, after=lambda e: print(f"Я трещу!: " if e else "Воспроизведение завершено"))
    except Exception as e:
        await ctx.send(f"Я трещу!")
        print(f"Ошибка: {e}")
@bot.command()
async def status(ctx, status_type: str, *, message: str):
    if discord.utils.get(ctx.author.roles, id=watchdog_role):
        status_mapping = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible,
        }
        activity = discord.Game(name=message)
        new_status = status_mapping.get(status_type.lower())

        if not new_status:
            await ctx.send("Ты трещишь на меня: online, idle, dnd, invisible.")
            return
        await bot.change_presence(status=new_status, activity=activity)
        await ctx.send(f"Done.")
    else:
        await ctx.send("Ты трещишь!")
bot.run(token)
