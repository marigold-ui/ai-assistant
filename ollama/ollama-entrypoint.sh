#!/bin/bash

/bin/ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready and pull model
sleep 2
MODEL="${OLLAMA_MODEL:-nomic-embed-text}"
echo "Pulling model: $MODEL"
ollama pull "$MODEL"

wait $OLLAMA_PID
