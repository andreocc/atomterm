FROM python:3.9-slim

WORKDIR /app

# Install curl, wget, unzip, tar for downloading Ollama
RUN apt-get update && apt-get install -y curl wget unzip tar && rm -rf /var/lib/apt/lists/*

# Download and install Ollama using the provided script
RUN curl -fsSL https://ollama.com/install.sh -o ollama_install.sh && \
    chmod +x ollama_install.sh && \
    ./ollama_install.sh && \
    ls -l /usr/local/bin/ollama

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Make the start script executable
RUN chmod +x start.sh

# Set the entrypoint to our script
CMD ["./start.sh"]
