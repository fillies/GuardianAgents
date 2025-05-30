import os
import json
import re
import discord
from dotenv import load_dotenv
import aiohttp
from fastapi import FastAPI, Request
import uvicorn
from threading import Thread

from fastapi import BackgroundTasks
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status
from pydantic import BaseModel
from typing import List, Dict
import asyncio
import nest_asyncio

class AssertInput(BaseModel):
    assert_: List[str]  # `assert` is a Python keyword, so use `alias`
    location: str

    class Config:
        fields = {'assert_': 'assert'}


class ModerationInput(BaseModel):
    message_id: str
    region: str
    legal_violation: Dict[str, List[str]]
    laws_violated: List[str]

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_NAME = os.getenv('DISCORD_GUILD')
INTRO_CHANNEL_ID = int(os.getenv('INTRO_CHANNEL_ID'))
CHAT_CHANNEL_ID = int(os.getenv('CHAT_CHANNEL_ID'))

# Persistent user data store
USER_DATA_FILE = "user_data.json"

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("Validation error!")
    print(f"Request body: {exc.body}")
    print(f"Validation errors: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.post("/new-moderation-decision")
async def receive_contetn_moderation(data: ModerationInput):
    print(data)
    asyncio.run_coroutine_threadsafe(
        process_legal_violation(data.model_dump()), client.loop
    )
    return {"status": "received"}


@app.post("/new-rules")
async def receive_new_rules(data: AssertInput):
    # message_id = "auto-generated-id"  # or extract from elsewhere if needed
    region = data.location
    rules = data.assert_

    asyncio.run_coroutine_threadsafe(
        send_dm_to_admin(region, rules),
        client.loop
    )

    print("📜 Received new rules update:")
    print(f"Message ID: {message_id}")
    print(f"Region: {region}")
    print("Rules:")
    for rule in rules:
        print(f" - {rule}")

    return {"status": "rules received and admin notified"}


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
        if author_id in user_data:
            country = user_data[author_id].get("country", "Unknown")
        else:
            country = "Unknown"

        message_id = str(message.id)
        message_content = message.content

        print("Country: " + country)
        print("Message ID: " + message_id)
        print("Message: " + message_content)

        # ✅ Make the API call
        async with aiohttp.ClientSession() as session:
            webhook_url = "http://81.169.159.230:7860/api/v1/webhook/1a6591da-6170-4e2c-94a9-7f92cc5ff775"
            payload = {
                "message_id": message_id,
                "location": country,
                "message": message_content
            }

            try:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        print("Successfully sent message to Langflow webhook.")
                    else:
                        print(f"Webhook call failed with status {response.status}")
            except Exception as e:
                print(f"Error calling webhook: {e}")

        if 'hi' in message.content.lower():
            await message.channel.send('Hi')
        await message.channel.send("Currently  there is content moderation in place")

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

async def send_dm_to_admin(country, rules):
    await client.wait_until_ready()  # Ensure the bot is connected
    admin_id = int(os.getenv("DISCORD_ADMIN_ID"))
    admin_user = await client.fetch_user(admin_id)

    if admin_user:
        rule_text = "\n".join([f"- {r}" for r in rules])
        dm_message = (
            f"📢 **New Rules Received**\n"
            f"**Country**: {country}\n"
            f"**Rules:**\n{rule_text}"
        )
        #f"**Message ID**: {message_id}\n"
        try:
            await admin_user.send(dm_message)
            print("✅ DM sent to admin.")
        except Exception as e:
            print(f"❌ Failed to send DM to admin: {e}")
    else:
        print("❌ Admin user not found.")

async def process_legal_violation(data):
    await client.wait_until_ready()

    message_id = int(data.get("message_id"))
    region = data.get("region", "Unknown")
    legal_violation = data.get("legal_violation", {})
    laws_violated = data.get("laws_violated", [])

    if not legal_violation:
        print(f"✅ No legal violations. Message {message_id} not deleted.")
        return

    try:
        channel = client.get_channel(CHAT_CHANNEL_ID)
        message = await channel.fetch_message(message_id)
        await message.delete()
        print(f"🗑️ Deleted message {message_id} due to legal violations.")

        # Construct human-readable reason
        violations = []
        for category, details in legal_violation.items():
            for item in details:
                violations.append(f"{category.replace('_', ' ').title()}: {item.replace('_', ' ').title()}")

        law_text = "\n".join([f"🔹 {law}" for law in laws_violated])
        reasons = "\n".join([f"• {v}" for v in violations])

        warning_message = (
            f"🚨 A message was removed due to legal concerns in **{region.title()}**.\n"
            f"**Violations:**\n{reasons}\n\n"
            f"**Laws Violated:**\n{law_text}"
        )

        await channel.send(warning_message)

    except Exception as e:
        print(f"❌ Failed to process legal violation: {e}")


async def start_fastapi():
    config = uvicorn.Config(app, host="0.0.0.0", port=8082, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    # Start FastAPI as background task
    asyncio.create_task(start_fastapi())
    # Start Discord bot
    await client.start(TOKEN)

if __name__ == "__main__":
    nest_asyncio.apply()  # Patch asyncio so Discord + FastAPI can coexist
    asyncio.run(main())
