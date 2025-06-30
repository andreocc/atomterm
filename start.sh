#!/bin/bash

# Start the Ollama server in the background
/usr/local/bin/ollama serve &

# Wait a moment for the server to initialize
sleep 5

# Pull the specified Ollama model
/usr/local/bin/ollama pull gemma3

# Start the Streamlit application
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
