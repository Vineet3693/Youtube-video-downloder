
#!/bin/bash

# YouTube Downloader App Setup Script
set -e

echo "🚀 Setting up YouTube Downloader App..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✅ Python version $python_version is compatible"
else
    echo "❌ Python 3.9+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install system dependencies (Ubuntu/Debian)
if command -v apt-get >/dev/null 2>&1; then
    echo "📋 Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg wget curl
fi

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p downloads
mkdir -p logs
mkdir -p temp

# Set permissions
chmod +x scripts/*.sh

# Install pre-commit hooks (if in development)
if [ -f ".pre-commit-config.yaml" ]; then
    echo "🔧 Setting up pre-commit hooks..."
    pip install pre-commit
    pre-commit install
fi

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

echo "✅ Setup complete!"
echo ""
echo "🎯 To start the application:"
echo "   source venv/bin/activate"
echo "   streamlit run app/main.py"
echo ""
echo "🌐 The app will be available at: http://localhost:8501"
