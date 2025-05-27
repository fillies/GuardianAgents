# Prova Evaluator

The **Prova Evaluator** is a component of the [GuardianAgents](https://github.com/fillies/GuardianAgents) project. It is responsible for storing and evaluating incoming classification results against the generated legal and ethical prolog rules.

---

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/fillies/GuardianAgents.git
cd GuardianAgents/prova-evaluator
```

## Running with Docker
You can build and run the Prova Evaluator using Docker for consistent, isolated execution.

### Step 1: Build the Docker Image
From the prova-evaluator directory:

```bash
docker build -t prova-evaluator .
```
This command builds the Docker image and tags it as prova-evaluator.

### Step 2: Run the Docker Container
Once the image is built, you can run the container with:

```bash
docker run --rm -it \
  --ulimit nproc=65535 \
  --ulimit nofile=65535:65535 \
  --pids-limit=-1 \
  -e SOME_ENV_VAR=value \
  -v $(pwd)/data:/app/data \
  -p 8081:8080 \
  prova-evaluator
```