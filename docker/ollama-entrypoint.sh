#!/bin/sh
set -e

echo "Starting Ollama server in background..."
/bin/ollama serve &
ollama_pid="$!"

echo "Waiting for Ollama API to be ready..."
until curl -s http://localhost:11434/api/version > /dev/null 2>&1; do
    sleep 2
done

echo "Ollama server ready, keeping server running..."
wait "$ollama_pid"
