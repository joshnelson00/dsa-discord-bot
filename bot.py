import os
import discord
import ollama_serve
from discord.ext import commands
from dotenv import load_dotenv
from ollama_serve import query_ollama
from question_serve import *
from user_info import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

ollama_serve.main()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Sorry, the command `{ctx.invoked_with}` is not found. Please check the available commands.")
    else:
        raise error

class problem_topic(discord.ui.Select):
    def __init__(self):
        options = get_topic_options()
        super().__init__(placeholder='Select a topic to practice', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_topic = self.values[0]
        view = self.view
        if isinstance(view, DSADropdownView):
            view.selected_topic = selected_topic
        await interaction.response.send_message(f'You selected topic: {selected_topic}', ephemeral=True)
        view.clear_items()
        view.add_item(problem_diff())
        await interaction.edit_original_response(view=view)

class problem_diff(discord.ui.Select):
    def __init__(self):
        options = get_difficulty_options()
        super().__init__(placeholder='Select a difficulty', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_difficulty = self.values[0]
        view = self.view
        if isinstance(view, DSADropdownView):
            view.selected_difficulty = selected_difficulty
            selected_topic = view.selected_topic
            problem = get_problem(selected_topic, selected_difficulty)
            if problem is None:
                await interaction.response.send_message(
                    "No results found for this question type in DB. Please try again.",
                    ephemeral=True,
                )
                return
            view.problem = problem
            await interaction.response.send_message(get_md_text(problem), ephemeral=True)
        else:
            await interaction.response.send_message("Something went wrong!", ephemeral=True)

class DSADropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.selected_topic = None
        self.selected_difficulty = None
        self.problem = None
        self.add_item(problem_topic())

    @discord.ui.button(label="Need a Hint?", style=discord.ButtonStyle.primary)
    async def ask_question(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.problem:
            await interaction.response.send_message(
                "Please select a topic and difficulty first!",
                ephemeral=True
            )
            return
        modal = AskLLMModal(problem_details=self.problem)
        await interaction.response.send_modal(modal)

class AskLLMModal(discord.ui.Modal, title="Ask About the Problem"):
    query = discord.ui.TextInput(
        label="Your Question",
        placeholder="Type your question about the problem here...",
        style=discord.TextStyle.long,
        required=True
    )

    def __init__(self, problem_details: dict):
        super().__init__()
        self.problem_details = problem_details

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_question = self.query.value
        problem = self.problem_details
        prompt = (
            f"You are a programming tutor. Answer the user's question related to the problem, but do **not** provide the solution in words or code.\n\n"
            f"Title: {problem['title']}\n"
            f"Description: {problem['description']}\n"
            f"Difficulty: {problem['difficulty']}\n\n"
            f"User's question: '{user_question}'\n\n"
            f"Instructions: Your response should help the user understand how to approach the problem without directly providing the solution to the original problem in words or code. "
            f"Provide hints or guidance on how they can solve it, but do not give the solution itself.\n"
            f"Limit your response to a maximum of 1800 characters."
        )
        response = query_ollama(prompt)
        await interaction.followup.send(
            f"**Your Question:** {user_question}\n\n{response}",
            ephemeral=True
        )

@bot.command()
async def practice_problem(ctx):
    await ctx.send("Select a topic to practice:", view=DSADropdownView())

@bot.command()
async def dsa(ctx):
    view = DSADropdownView()
    await ctx.send("Practice a DSA Question:", view=view)

@bot.command()
async def add_user(ctx, username: str = None):
    if username is None or not username.strip():
        await ctx.send(f"Please provide a valid username, {ctx.author.mention}.")
        return
    guild_id = ctx.guild.id
    key = f"server:{guild_id}:users"
    existing_usernames = r.lrange(key, 0, -1)
    if username.encode() in existing_usernames:
        await ctx.send(f"Username `{username}` already exists in the database.")
        return
    if leetcode_user_exists(username):
        r.rpush(key, username)
        await ctx.send(f"{ctx.author.mention} added Leetcode username `{username}`!")
    else:
        await ctx.send("That Leetcode username doesn't exist!")

@bot.command()
async def remove_user(ctx, username: str):
    if not username:
        await ctx.send("Please provide a username to remove.")
        return
    guild_id = ctx.guild.id
    key = f"server:{guild_id}:users"
    removed_count = r.lrem(key, 0, username)
    if removed_count > 0:
        await ctx.send(f"Username `{username}` has been removed from the leaderboard.")
    else:
        await ctx.send(f"Username `{username}` not found in the leaderboard.")

@bot.command()
async def leaderboard(ctx):
    guild_id = ctx.guild.id
    key = f"server:{guild_id}:users"
    usernames = r.lrange(key, 0, -1)
    valid_usernames = [username for username in usernames if username.strip()]
    if not valid_usernames:
        await ctx.send("No valid usernames have been added yet!")
        return
    formatted_usernames = "\n* ".join(valid_usernames)
    await ctx.send(get_leetcode_leaderboard(valid_usernames))

bot.run(TOKEN)
