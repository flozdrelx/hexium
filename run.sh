#!/bin/bash
cd Scripts 2>/dev/null || echo "Already in dir or dir doesn't exists."
if [ ! -d "venv" ]; then
    echo "Creating venv..."
    python3 -m venv venv > /dev/null 2>&1
fi
echo "Installing packages, please wait..."
source venv/bin/activate && pip install -r requirements.txt > /dev/null 2>&1
echo "Ready!"
python main.py