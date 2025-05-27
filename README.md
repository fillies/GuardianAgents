# GuardianAgents

Repository for the AgentX Competition at Berkeley RDI.

The bot connects to the Discord server `GuardianAgentsDemo` (join [here](https://discord.gg/your-invite-link)) and manages new user onboarding. It also integrates with Langflow for moderation and rule generation (integration to be implemented in `on_message`).

## ✨ Features

- **Dynamic legal rule generation**  
  Automatically generates moderation rules tailored to each user's country of origin, leveraging large language models (LLMs) and geopolitical context.

- **Ethical and legal content validation**  
  Evaluates user messages against a hybrid framework of ethical standards and jurisdiction-specific legal norms to ensure safe and compliant interactions.

- **Explainable content moderation**  
  Delivers transparent and interpretable moderation decisions by combining LLM-driven analysis with rule-based evaluations — enabling trust and auditability.


## 📁 Project Structure

The repository contains three main folders, each representing a part of the application:

- **`discord-bot/`** – Contains the code for the Discord bot, including onboarding logic, message handling, and user role management.
- **`langflow-agent/`** – Exported Langflow agent flow used to generate moderation decisions and dynamic rules (integration pending).
- **`prova-evaluator/`** – A rule-based evaluation module ("Prova") for assessing user messages against predefined criteria.
