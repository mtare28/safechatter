#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "--- 1. Installing Ollama and its dependencies ---"
sudo apt-get update
sudo apt-get install lshw -y
curl -fsSL https://ollama.com/install.sh | sh

echo ""
echo "--- 2. Installing the safechatter_tweek Python package ---"
pip install .

echo ""
echo "--- Installation Complete! ---"
echo "You may need to start the Ollama service if it is not already running."