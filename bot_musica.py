import discord
from discord.ext import commands
from pytube import YouTube
import json
import datetime
import os

intents = discord.Intents.all()

try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        token = config.get('token')
        if token is None:
            raise ValueError('Token não encontrado no arquivo config.json')
except FileNotFoundError:
    print('Arquivo config.json não encontrado')
    sys.exit(1)  # Termina a execução do programa
except json.JSONDecodeError:
    print('Erro ao decodificar o arquivo config.json')
    sys.exit(1)  # Termina a execução do programa
except ValueError as e:
    print(e)
    sys.exit(1)  # Termina a execução do programa

bot = commands.Bot(command_prefix='/', intents=intents)

channel_id = 1181632907371094049

FFMPEG_OPTIONS = {
    'options': '-vn',  # Desativa a parte de vídeo do stream, deixando apenas o áudio
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',  # Reconecta se a conexão for perdida
}

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
            if not author_channel:
                await ctx.send("Você precisa estar em um canal de voz para usar este comando.")
                return

            voice_channel = await author_channel.connect()

        # Criar objeto YouTube
        yt = YouTube(url)

        # Obter a melhor stream de áudio disponível
        audio_stream = yt.streams.filter(only_audio=True).first()

        # Baixar o áudio
        audio_file_path = os.path.join(os.getcwd(), audio_stream.title + ".mp4")
        audio_stream.download(output_path=os.getcwd(), filename=audio_stream.title)
        audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=audio_file_path, **FFMPEG_OPTIONS), volume=0.5)

        # Reproduzir o áudio no canal de voz
        print("Before playing audio")
        await voice_channel.play(audio_source, after=lambda e: print('done', e))
        print("After playing audio")

        await ctx.send(f'Tocando: {yt.title}')

    except Exception as e:
        print(f'Erro durante a reprodução: {e}')
        await ctx.send('Ocorreu um erro durante a reprodução.')

@bot.command()
async def stop(ctx):
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_channel and voice_channel.is_connected():
        await voice_channel.disconnect()

bot.run(token)