import os
import discord # type: ignore
import ollama_serve
from discord.ext import commands # type: ignore
from discord import ui # type: ignore
from dotenv import load_dotenv
from ollama_serve import get_practice_question
from modals import *
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

ollama_serve.main()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        await bot.tree.sync()
        print("Commands synced successfully.")
        for command in await bot.tree.fetch_commands():
            print(f"Command: {command.name}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.command()
async def dsa(ctx):
    #Sends a message with our dropdown containing colours

    view = dsa_dropdown_view()
    # Sending a message containing our view
    await ctx.send('Practice a DSA Question:', view=view)

bot.run(TOKEN)
