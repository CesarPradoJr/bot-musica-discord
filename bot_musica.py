import discord
from discord.ext import commands
from pytube import YouTube
import json
import datetime

intents = discord.Intents.all()

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

bot = commands.Bot(command_prefix='/', intents=intents)

channel_id = 1181632907371094049

@bot.event
async def on_ready():
    print(f'{bot.user.name} está conectado! hora:{datetime.datetime.now()}')

    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s): {datetime.datetime.now()}')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

    channel = bot.get_channel(channel_id)

    if channel:
        # Envia a mensagem
        await channel.send(f'{bot.user.name} está online!')

@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello world!")

@bot.command()
async def play(ctx, url):
    voice_channel = ctx.voice_client

    try:
        # Verificar se o bot está em um canal de voz
        if not voice_channel or not voice_channel.is_connected():
            # Se não estiver conectado, conecte-se ao canal do autor da mensagem
            author_channel = ctx.author.voice.channel
            voice_channel = await author_channel.connect()

        # Criar objeto YouTube
        yt = YouTube(url)

        # Obter a melhor stream de áudio disponível
        audio_stream = yt.streams.filter(only_audio=True).first()

        # Baixar o áudio
        audio_stream.download()

        # Reproduzir o áudio no canal de voz
        voice_channel.play(discord.FFmpegPCMAudio(audio_stream.title + ".webm"), after=lambda e: print('done', e))

        await ctx.send(f'Tocando: {yt.title}')

    except Exception as e:
        print(f'Erro durante a reprodução: {e}')
        await ctx.send('Ocorreu um erro durante a reprodução.')

@bot.command()
async def stop(ctx):
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_channel and voice_channel.is_connected():
        await voice_channel.disconnect()

bot.run('MTIwNTE5ODk2NzM2MTYzNDMxNQ.Gf43YZ.08OnzUm8TuCkrZHb6jtD5Z63U2f_NhK-h--8OY')