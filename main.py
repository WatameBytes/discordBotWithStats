import asyncio
import discord
import os
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from discord.ext import commands

# Define the bots intents, which must be enabled in the Discord Bot Developer Portal
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.dm_messages = True

# Initialize bot with the defined intents and use '$' for its commands
bot = commands.Bot(command_prefix='$', intents=intents)

# Limit who the bot will listen, to prevent unauthorized use
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID"))  # Ensure it's an integer


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')


# Checks if the command author is the authorized user
def is_authorized(ctx):
    return ctx.author.id == AUTHORIZED_USER_ID


# Construct the nickname with percentages and return the string
def construct_nickname(harris_percentage, trump_percentage):
    nickname = f"🔵{harris_percentage}%/🔴{trump_percentage}%"

    return nickname


# $random command used for debugging, by generating a random number and updating the
# bot nickname in the guild (server)
@bot.command(name='random')
async def random_command(ctx):
    if not is_authorized(ctx):
        await ctx.send("You are not authorized to use this command.")
        return

    # Generate random percentages
    harris_percentage = random.randint(0, 100)
    trump_percentage = 100 - harris_percentage

    new_nickname = construct_nickname(harris_percentage, trump_percentage)

    guild = ctx.guild
    if guild:
        try:
            await guild.me.edit(nick=new_nickname)
            await ctx.send(f"Updated bot nickname to '{new_nickname}'")
        except discord.Forbidden:
            await ctx.send("I don't have permission to change my nickname in this server.")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to update nickname. Error: {e}")
    else:
        await ctx.send("Could not find the guild.")


# When an authorized user sends 'update <server_id>' via DM, it will run update_nickname_with_data
@bot.event
async def on_message(message):
    # Avoid responding to ourselves
    if message.author == bot.user:
        return

    # Check if message is a DM
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id == AUTHORIZED_USER_ID:
            content = message.content.strip()
            if content.lower().startswith("update"):
                parts = content.split()
                if len(parts) == 2:
                    guild_id_str = parts[1]
                    try:
                        guild_id = int(guild_id_str)
                        # Run the data fetching code and update nickname
                        await update_nickname_with_data(message.author, guild_id)
                    except ValueError:
                        await message.author.send("Invalid guild ID. Please provide a valid guild (server) ID.")
                else:
                    await message.author.send("Please provide a guild ID. Usage: 'update <guild_id>'")
    else:
        # Process commands if the message is not a DM
        await bot.process_commands(message)


# Scraps data from https://projects.fivethirtyeight.com/2024-election-forecast/ and grabs the presidential
# election forcast
async def update_nickname_with_data(user, guild_id):
    # Fetch data
    data = await fetch_election_data()
    if data:
        # Get the latest percentages
        candidates = data["candidates"]
        harris_percentage = candidates.get("Harris", 0)
        trump_percentage = candidates.get("Trump", 0)

        # Construct the new nickname
        new_nickname = construct_nickname(harris_percentage, trump_percentage)

        # Update the bots nickname in the guild
        guild = bot.get_guild(guild_id)

        if guild:
            try:
                await guild.me.edit(nick=new_nickname)
                # Send confirmation to the user
                await user.send(f"Updated bot nickname to '{new_nickname}' in guild '{guild.name}'")
            except discord.Forbidden:
                await user.send(f"Failed to update nickname in guild '{guild.name}'. Missing permissions.")
            except discord.HTTPException as e:
                await user.send(f"Failed to update nickname in guild '{guild.name}'. Error: {e}")
        else:
            await user.send("Could not find the guild with the provided ID or I'm not a member of it.")
    else:
        await user.send("Failed to fetch election data.")


def extract_odds(text):
    """Extract numeric odds value from text"""
    try:
        return int(text.strip('%'))
    except ValueError:
        # Handle "less than 1%" case
        if "less than 1" in text.lower():
            return 0
        print(f"Could not parse odds value: {text}")
        return None


def fetch_election_data_sync():
    url = "https://projects.fivethirtyeight.com/2024-election-forecast/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        odds_container = soup.find('div', id='odds-text')
        if not odds_container:
            print("Could not find odds container")
            return None

        prediction_data = {
            "timestamp": datetime.now().isoformat(),
            "candidates": {},
            "total_simulations": 100,
            "no_winner_chance": 0,
            "source_url": url
        }

        # Extract odds
        rep_div = odds_container.find('div', class_='rep')
        if rep_div:
            prediction_data["candidates"]["Trump"] = int(rep_div.find('span', class_='odds').text.strip('%'))

        dem_div = odds_container.find('div', class_='dem')
        if dem_div:
            prediction_data["candidates"]["Harris"] = int(dem_div.find('span', class_='odds').text.strip('%'))

        print(f"Fetched data at {prediction_data['timestamp']}: {prediction_data}")  # Debugging output

        return prediction_data

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


async def fetch_election_data():
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, fetch_election_data_sync)
    return data


# Run the bot
bot.run(os.getenv("TOKEN"))
