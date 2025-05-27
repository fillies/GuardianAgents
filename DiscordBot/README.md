# GuardianAgents

Repository for the AgentX Competition at Berkeley RDI.

The bot connects to the Discord server **GuardianAgentsDemo** ([join here](https://discord.gg/mM95jTty)) and manages new user onboarding. It also integrates with Langflow for moderation and rule generation (integration to be implemented in `on_message`).

## ✨ Features

- Welcomes new members and assigns a "Quarantine" role until proper introduction.
- Expects a specific format for introductions and assigns the "Member" role upon verification.
- Stores user data persistently in a JSON file.
- Responds to messages and logs country-based metadata for future moderation.
- Prepares messages to be sent to Langflow (integration point marked in code).

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/GuardianAgents.git
cd GuardianAgents/DiscordBot
```

## 🚀 Getting Started

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
DISCORD_TOKEN=your_bot_token_here
DISCORD_GUILD=GuardianAgentsDemo
INTRO_CHANNEL_ID=your_intro_channel_id
CHAT_CHANNEL_ID=your_chat_channel_id
```

## 🐳 Docker Setup

### 3. Build the Docker Image

```bash
docker build -t guardian-bot .
```

### 4. Run the Container

```bash
docker run -d -p 8082:8082 --name guardian-bot --env-file .env guardian-bot
```