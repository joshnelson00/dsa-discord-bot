import os
import discord
import ollama_serve
from discord.ext import commands
from discord import ui
from dotenv import load_dotenv
from ollama_serve import get_practice_question

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

ollama_serve.main()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

class TestModal(ui.Modal, title='Practice DSA Question'):
    topic = ui.TextInput(
        label='Topic',
        placeholder='ex: Arrays',
    )
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Defer the initial response to prevent timing out
            await interaction.response.defer(ephemeral=True)

            # Get the topic and generate the question
            question_topic = self.topic.value
            result = get_practice_question(question_topic)  # Ensure this returns a string

            # Send the actual response
            await interaction.followup.send(result, ephemeral=True)

        except Exception as e:
            print(f"Error in on_submit: {e}")
            # Send an error message as a follow-up
            try:
                await interaction.followup.send(
                    "An error occurred while submitting your response. Please try again.",
                    ephemeral=True
                )
            except discord.HTTPException as http_exc:
                print(f"Failed to send error message: {http_exc}")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        await bot.tree.sync()
        print("Commands synced successfully.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.command(name="broadcast")
async def broadcast_message(ctx, *, message: str):
    try:
        await ctx.send(message)
        print(f"Broadcast message sent in {ctx.guild.name} in #{ctx.channel.name}")
    except Exception as e:
        print(f"Failed to send message in {ctx.guild.name}: {e}")

@bot.command(name="practice_question")
async def practice_question(ctx, *, topic: str):
    result = get_practice_question(topic)
    await ctx.send(result)

@bot.tree.command(name="practice", description="Submit feedback")
async def feedback(interaction: discord.Interaction):
    await interaction.response.send_modal(TestModal())

bot.run(TOKEN)
