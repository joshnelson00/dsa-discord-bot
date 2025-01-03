import asyncio
import os
import discord  # type: ignore
from discord.ext import commands  # type: ignore
from dotenv import load_dotenv
from question_serve import get_topic_options, get_difficulty_options, get_md_text, get_ai_problem, get_problem
from user_info import *
from db import r

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # Iterate through all the servers the bot is in to ensure the rules channel exists
    for guild in bot.guilds:
        await ensure_rules_channel(guild)


@bot.event
async def on_guild_join(guild):
    """When the bot joins a new server, create the rules channel."""
    await ensure_rules_channel(guild)


async def ensure_rules_channel(guild):
    # Check if the "rules" channel exists
    rules_channel = discord.utils.get(guild.text_channels, name="AL_G_RITHM-bot-help")
    if rules_channel:
        return

    # Create the "rules" channel
    try:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False)  # Make it read-only
        }
        help_channel = await guild.create_text_channel("AL_G_RITHM-bot-help", overwrites=overwrites)
        
        # Send the Markdown message
        await help_channel.send("""
# How to Use AL_G_RITHM

Welcome to the **AL_G_RITHM** Bot! This bot helps you practice Data Structures and Algorithms (DSA) questions, get hints, and view leaderboards. Here's how to use it:

## Commands

### 1.`!leetcode_problem` :jigsaw:
Practice a **Leetcode** DSA problem.
- Type `!leetcode_problem`.
- Select a topic and difficulty.
- Get a problem to solve.

### 2.`!ai_problem` :robot:
Practice an **AI-Generated** DSA problem.
- Type `!ai_problem`.
- Select a topic and difficulty.
- Get a problem to solve.

### 3. `!add_user <username>` :white_check_mark:
Add your **Leetcode** username to the leaderboard.
- Type `!add_user <your_username>`.
- The bot will verify and add your username.

### 4. `!remove_user <username>` :no_entry:
Remove your **Leetcode** username from the leaderboard.
- Type `!remove_user <your_username>`.

### 5. `!leaderboard` :trophy:
View the top Leetcode problem solvers in the server.
- Type `!leaderboard`.
- The bot shows the top performers.
- The leaderboard is synced to your account on Leetcode and only tracks **Leetcode** problems, not AI problems!


## Getting Started :rocket:

1. Type `!leetcode_problem` or `!ai_problem` to get started.
2. Select the topic and difficulty to get a problem. This may take up to 30 seconds :hourglass_flowing_sand:.
3. If you need help, press the "Need a Hint?" button :bulb:.
4. Add your Leetcode username to the leaderboard with `!add_user <username>`. (Make sure that you have created an account!)

## Rules

1. **Be respectful** :pray: : Be polite to others.
2. **Avoid spamming** :no_entry_sign: : Use commands when needed.
3. **Follow server rules** :scroll: : Adhere to server and Discord rules.

The bot is meant to be fun and educational! :mortar_board: Let's improve our DSA skills! :muscle:
""")
        
    except Exception as e:
        print(f"Failed to create 'rules' channel in {guild.name}: {e}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Inform the user that the command is not found
        await ctx.send(
            f"Sorry, {ctx.author.mention}, the command `{ctx.invoked_with}` is not recognized. "
            "Please use `!help` to see the list of available commands."
        )
    else:
        # Re-raise other errors to avoid hiding them
        raise error

# Dropdown for problem topic selection
class problem_topic(discord.ui.Select):
    def __init__(self, source: str):
        options = get_topic_options()
        self.source = source
        super().__init__(placeholder='Select a topic to practice', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_topic = self.values[0]  # Store the selected topic
        view = self.view  # Access the parent view
        if isinstance(view, DSADropdownView):
            view.selected_topic = selected_topic  # Save data to the view

        await interaction.response.send_message(f'You selected topic: {selected_topic}', ephemeral=True)

        view.clear_items()
        view.add_item(problem_diff(source=self.source))
        await interaction.edit_original_response(view=view)


# Dropdown for problem difficulty selection
class problem_diff(discord.ui.Select):
    def __init__(self, source: str):
        options = get_difficulty_options()
        self.source = source
        super().__init__(placeholder='Select a difficulty', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Step 1: Defer the response
        await interaction.response.defer(ephemeral=True)

        # Step 2: Perform async tasks like sleeping
        await asyncio.sleep(2)  # Simulate a delay (e.g., waiting for data)

        # Step 3: Send the follow-up message
        selected_difficulty = self.values[0]
        view = self.view  # Access the parent view
        if self.source == "leetcode":
            view.selected_difficulty = selected_difficulty
            selected_topic = view.selected_topic
            problem = get_problem(selected_topic, selected_difficulty) # Here
            if problem is None:
                await interaction.followup.send(
                    "No results found for this question type in DB. Please try again.",
                    ephemeral=True,
                )
                return

            # Save the problem details to the view
            view.problem = problem

            try:
                await interaction.followup.send(get_md_text(problem), ephemeral=True)
            except discord.errors.NotFound:
                # Interaction expired, handle it accordingly
                print("Interaction expired, unable to send message.")
                await interaction.followup.send("The interaction expired. Please try again.", ephemeral=True)

        elif self.source == "ai":
            view.selected_difficulty = selected_difficulty
            selected_topic = view.selected_topic
            problem = get_ai_problem(selected_topic, selected_difficulty)
            if problem is None:
                await interaction.followup.send(
                    "No results found for this question type in DB. Please try again.",
                    ephemeral=True,
                )
                return

            # Save the problem details to the view
            view.problem = problem

            try:
                await interaction.followup.send(get_md_text(problem), ephemeral=True)
            except discord.errors.NotFound:
                # Interaction expired, handle it accordingly
                print("Interaction expired, unable to send message.")
                await interaction.followup.send("The interaction expired. Please try again.", ephemeral=True)
        else:
            await interaction.followup.send("Something went wrong!", ephemeral=True)



# Dropdown view containing both dropdowns
class DSADropdownView(discord.ui.View):
    def __init__(self, source: str, timeout: float = 300.0):  # Timeout extended to 5 minutes
        super().__init__(timeout=timeout)
        self.selected_topic = None
        self.selected_difficulty = None
        self.source = source
        self.problem = None
        self.add_item(problem_topic(source=source))  # Add the topic dropdown

    # Button to trigger the modal for asking questions
    @discord.ui.button(label="Need a Hint?", style=discord.ButtonStyle.primary)
    async def ask_question(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.problem:
            await interaction.response.send_message(
                "Please select a topic and difficulty first!",
                ephemeral=True
            )
            return

        # Pass the selected problem to the modal
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
        self.problem_details = problem_details  # Pass problem details to the modal

    async def on_submit(self, interaction: discord.Interaction):
    # Acknowledge the interaction immediately to prevent timeout
        await interaction.response.defer(ephemeral=True)

        # Construct the prompt with the user's query and problem details
        user_question = self.query.value
        problem = self.problem_details

        prompt = (
        f"You are a programming tutor. Answer the user's question related to the problem, but do **not** provide the solution in words or code.\n\n"
        f"Title: {problem['title']}\n"
        f"Description: {problem['description']}\n"
        f"Difficulty: {problem['difficulty']}\n\n"
        f"User's question: '{user_question}'\n\n"
        f"Instructions: Your response should help the user understand how to approach the problem without directly providing the solution to the orignal problem in words or code."
        f"Provide hints or guidance on how they can solve it, but do not give the solution itself.\n"
        f"Limit your response to a maximum of 1800 characters."
        )
        # Query Ollama
        response = get_md_text(prompt)

        # Follow-up response with the LLM's answer
        await interaction.followup.send(
            f"**Your Question:** {user_question}\n\n{response}",
            ephemeral=True
        )

# Command to trigger the dropdown
@bot.command()
async def leetcode_problem(ctx):
    # Sends a message with our dropdown containing topics
    view = DSADropdownView(source="leetcode")
    await ctx.send("Practice a DSA Question:", view=view)

@bot.command()
async def ai_problem(ctx):
    # Sends a message with our dropdown containing topics
    view = DSADropdownView(source="ai")
    await ctx.send("Practice a DSA Question:", view=view)

@bot.command()
async def add_user(ctx, username: str = None):
    username_check = get_user_data(username)

    if username is None or not username.strip() or username_check is False:
        await ctx.send(f"Please provide a valid username, {ctx.author.mention}.")
        return

    user_id = ctx.author.id  # Discord user ID
    guild_id = ctx.guild.id  # Server ID (to avoid conflicts across servers)

    # Create a key specific to the guild
    key = f"server:{guild_id}:users"

    # Check if the username already exists in the list
    existing_usernames = r.lrange(key, 0, -1)  # Get all usernames in the list
    if username.encode() in existing_usernames:  # Check if username exists
        await ctx.send(f"Username `{username}` already exists in the database.")
        return

    # Add username if it doesn't exist
    r.rpush(key, username)
    await ctx.send(f"Added Leetcode username `{username}` for user {ctx.author.mention}!")

@bot.command()
async def remove_user(ctx, username: str):
    # Ensure the username is provided
    if not username:
        await ctx.send("Please provide a username to remove.")
        return

    guild_id = ctx.guild.id  # Get the current server's ID
    key = f"server:{guild_id}:users"  # The key used in Redis to store usernames

    # Remove the specified username from the Redis list
    removed_count = r.lrem(key, 0, username)

    # Check if the username was removed
    if removed_count > 0:
        await ctx.send(f"Username `{username}` has been removed from the list.")
    else:
        await ctx.send(f"Username `{username}` not found in the list.")

@bot.command()
async def leaderboard(ctx):
    guild_id = ctx.guild.id  # Get the current server's ID
    key = f"server:{guild_id}:users"  # The key used in Redis to store usernames

    # Retrieve all usernames stored in Redis for this guild
    usernames = r.lrange(key, 0, -1)  # Gets the entire list of usernames

    # Filter out any invalid usernames (None or empty)
    valid_usernames = [username for username in usernames if username.strip()]

    if not valid_usernames:
        await ctx.send("No valid usernames have been added yet!")
        return
    
    leaderboard = get_desktop_leetcode_leaderboard(valid_usernames)
    
    # Send the leaderboard
    await ctx.send(leaderboard)

bot.run(TOKEN)