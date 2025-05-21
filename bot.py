import os
import json
import re
import discord
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_NAME = os.getenv('DISCORD_GUILD')
INTRO_CHANNEL_ID = int(os.getenv('INTRO_CHANNEL_ID'))
CHAT_CHANNEL_ID = int(os.getenv('CHAT_CHANNEL_ID'))

# Persistent user data store
USER_DATA_FILE = "user_data.json"

# Load user data from file
if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        user_data = json.load(f)
else:
    user_data = {}

# Save user data to file
def save_user_data():
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=4)

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    for guild in client.guilds:
        if guild.name == GUILD_NAME:
            print(f'Connected to guild: {guild.name} (id: {guild.id})')
            break

@client.event
async def on_member_join(member):
    guild = member.guild
    intro_channel = client.get_channel(INTRO_CHANNEL_ID)

    quarantine_role = discord.utils.get(guild.roles, name="Quarantine")
    if quarantine_role:
        await member.add_roles(quarantine_role)

    if intro_channel:
        await intro_channel.send(
            f"👋 Welcome {member.mention}!\n"
            f"Please introduce yourself here with the country you are from and your age to unlock access to the rest of the server! Use this Format: 'Name: Jan, Country: Germany, Age: 10'"
        )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id == CHAT_CHANNEL_ID:
        author_id = str(message.author.id)
        print(message)
        if author_id in user_data:
            country = user_data[author_id].get("country", "Unknown")
        else:
            country = "Unknown"

        print("Country: "+ country)
        print("Message ID: " + str(message.id))
        print("Message: "+ str( message.content))
        #make call to langflow with country message.id and content
        #await message.channel.send(f"{message.author.display_name} is from {country}")

        if 'hi' in message.content.lower():
            await message.channel.send('Hi')
        await message.channel.send("Currently no moderation is in place")

    if message.channel.id == INTRO_CHANNEL_ID:
        member = message.author
        guild = message.guild

        quarantine_role = discord.utils.get(guild.roles, name="Quarantine")
        member_role = discord.utils.get(guild.roles, name="Member")

        pattern = r"Name:\s*(.+?),\s*Country:\s*(.+?),\s*Age:\s*(\d+)"
        match = re.search(pattern, message.content, re.IGNORECASE)

        if match:
            name, country, age = match.groups()

            user_data[str(member.id)] = {
                "discord_name": member.name,
                "name": name.strip(),
                "country": country.strip(),
                "age": int(age.strip())
            }
            save_user_data()

            if quarantine_role in member.roles:
                await member.remove_roles(quarantine_role)
                if member_role:
                    await member.add_roles(member_role)

            await message.channel.send(
                f"Thanks for introducing yourself, {member.mention}! You now have access to the chat."
            )
        else:
            await message.channel.send(
                f"{member.mention}, please use the correct format: `Name: Jan, Country: Germany, Age: 10`"
            )

client.run(TOKEN)
