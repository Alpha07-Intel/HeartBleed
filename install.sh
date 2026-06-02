#!/bin/bash

# HeartBleed Installation Script
# Supports: Linux and Termux (Android)

set -e

echo "🩸 Initializing HeartBleed Installation..."

# 1. Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "⚠️ Warning: HeartBleed is optimized for Python 3.11+. You are running $PYTHON_VERSION."
fi

# 2. Check for Pip
if ! command -v pip3 &> /dev/null; then
    echo "⚠️ Pip3 not found. Attempting to install..."
    if command -v pkg &> /dev/null; then
        pkg install python-pip -y
    elif command -v apt &> /dev/null; then
        sudo apt update && sudo apt install python3-pip -y
    fi
fi

# 3. Handle Termux specifics and Rust/Maturin issues for Pydantic
echo "📦 Installing dependencies..."
if [[ "$OSTYPE" == "linux-android" ]]; then
    echo "📱 Termux environment detected. Applying compatibility patches..."
    # We install dependencies individually to ensure pydantic v1 is prioritized
    pip3 install requests rich typer "pydantic<2.0" beautifulsoup4 pillow imagehash --quiet
else
    pip3 install -r requirements.txt --quiet
fi

# 4. Set up directory structure (just in case)
mkdir -p exports/reports

# 5. Finalize
echo "✅ Installation Complete!"
echo ""
echo "🚀 To start using HeartBleed, run:"
echo "   python3 -m heartbleed.main scan [username]"
echo ""
echo "Example:"
echo "   python3 -m heartbleed.main scan johndoe"
echo ""
echo "For help:"
echo "   python3 -m heartbleed.main --help"
