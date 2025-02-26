#!/bin/bash

# Start venv
source venv/bin/activate

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Python не встановлений. Встановіть Python і спробуйте знову."
    exit 1
fi

# Встановлення необхідних бібліотек
# pip3 install -r requirements.txt

# Запуск main.py
python3 main.py

call deactivate
