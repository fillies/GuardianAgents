# bot.py
import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_NAME = os.getenv('DISCORD_GUILD')
INTRO_CHANNEL_ID = int(os.getenv('INTRO_CHANNEL_ID'))  # Must be an integer
CHAT_CHANNEL_ID = int(os.getenv('CHAT_CHANNEL_ID'))  # Must be an integer

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

    print(message)
    if message.channel.id == CHAT_CHANNEL_ID:

        if 'hi' in message.content:
            response = 'Hi'
            await message.channel.send(response)
        await message.channel.send("Currently no moderation is in place")

    if message.channel.id == INTRO_CHANNEL_ID:
        member = message.author
        guild = message.guild

        quarantine_role = discord.utils.get(guild.roles, name="Quarantine")
        member_role = discord.utils.get(guild.roles, name="Member")

        if quarantine_role in member.roles:
            await member.remove_roles(quarantine_role)
            if member_role:
                await member.add_roles(member_role)
            await message.channel.send(
                f"Thanks for introducing yourself, {member.mention}! You now have access to the chat."
            )

client.run(TOKEN)
