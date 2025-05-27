# Langflow Agent Flow

This repository contains a **Langflow agent flow** designed to be imported into the open-source standalone Docker deployment of [Langflow](https://github.com/logspace-ai/langflow).

## 📦 Contents

- `GuardianAgents_with_Webhook.json` – A pre-built Langflow flow file you can import and run.

## 🚀 How to Use

1. **Set up Langflow with Docker**  
   Follow the official guide to run Langflow via Docker:  
   📖 [Langflow Docker Deployment Guide](https://docs.langflow.org/deployment-docker)

2. **Import the Flow**
   - Once Langflow is running locally (typically at `http://localhost:7860`), open the web interface.
   - Upload the `GuardianAgents_with_Webhook.json` file from this repository.
   - Add the needed api keys to the agents in the flow.

3. **Run the Flow**  
   Customize or run the flow directly within the Langflow UI.

## 🔗 Resources

- [Langflow Documentation](https://docs.langflow.org/)
- [Langflow GitHub Repository](https://github.com/logspace-ai/langflow)