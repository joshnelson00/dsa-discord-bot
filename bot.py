import os
import discord
import ollama_serve
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

ollama_serve.main()

print(ollama_serve.get_response("Arrays"))




intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.command(name="broadcast")
async def broadcast_message(ctx, *, message: str):
    try:
        await ctx.send(message)
        print(f"Broadcast message sent in {ctx.guild.name} in #{ctx.channel.name}")
    except Exception as e:
        print(f"Failed to send message in {ctx.guild.name}: {e}")

@bot.command(name="question")
async def question(ctx, *, question: str):
    pass

bot.run(TOKEN)