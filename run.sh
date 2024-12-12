#!/bin/sh

set -e

# 1. Create venv
uv venv -p 3.12 --allow-existing

# 2. Activate venv
. .venv/bin/activate

# 3. Install dependencies
uv pip install -r requirements.txt

# 4. Run Python script
python3 main.py

# 5. Deactivate venv
deactivate
