#!/bin/bash
# Script to make file-agent globally accessible

set -e

echo "🔧 Installing file-agent globally..."

# Get the project directory (where this script is located)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first."
    echo "   Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing/updating dependencies..."
poetry install

# Get the Poetry virtualenv path
VENV_PATH=$(poetry env info --path)
BIN_PATH="$VENV_PATH/bin/file-agent"

if [ ! -f "$BIN_PATH" ]; then
    echo "❌ file-agent not found in Poetry virtualenv at: $BIN_PATH"
    exit 1
fi

# Create ~/.local/bin if it doesn't exist
LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"

# Create symlink
echo "🔗 Creating symlink..."
ln -sf "$BIN_PATH" "$LOCAL_BIN/file-agent"
chmod +x "$LOCAL_BIN/file-agent"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo ""
    echo "⚠️  ~/.local/bin is not in your PATH."
    echo "   Add this line to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "   Then run: source ~/.bashrc  (or source ~/.zshrc)"
    echo ""
fi

# Verify installation
if command -v file-agent &> /dev/null; then
    echo "✅ file-agent installed successfully!"
    echo "   Try running: file-agent --version"
else
    echo "✅ Symlink created, but you may need to:"
    echo "   1. Add ~/.local/bin to your PATH (see above)"
    echo "   2. Reload your shell: source ~/.bashrc"
fi
