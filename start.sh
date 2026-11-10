#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# frontend/dist is not committed, so build the UI on first launch
if [ ! -f "$DIR/frontend/dist/index.html" ]; then
    if command -v npm >/dev/null 2>&1; then
        echo "Building web interface..."
        (cd "$DIR/frontend" && npm ci && npm run build)
    else
        echo "⚠️  npm not found: only the API will be available. Install Node.js 20+ to get the web UI."
    fi
fi

cd "$DIR/backend"

if [ ! -d "venv" ]; then
    echo "Creating virtualenv..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "🚀 Starting OmniTrace on http://127.0.0.1:8000 ..."
python run.py
