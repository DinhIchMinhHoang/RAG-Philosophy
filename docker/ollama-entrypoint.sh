#!/bin/bash
set -e

echo "Starting Ollama server in background..."
exec /bin/ollama serve &

echo "Waiting for Ollama API to be ready..."
until curl -s http://localhost:11434/api/version > /dev/null 2>&1; do
    sleep 2
done

echo "Checking if glm-ocr model exists..."
if ! ollama list | grep -q "^glm-ocr"; then
    echo "Pulling glm-ocr model..."
    ollama pull glm-ocr
    echo "glm-ocr model ready"
else
    echo "glm-ocr model already exists"
fi

echo "Ollama setup complete, keeping server running..."
wait