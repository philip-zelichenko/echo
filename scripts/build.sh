#!/bin/bash

# Ensure we're in the project root
cd "$(dirname "$0")/.."

echo "🚀 Building Echo Assistant..."

# Install dependencies
poetry install

# Build the executable
poetry run python scripts/build_app.py

# Show completion message
echo "
✅ Build complete!

The following files have been created:
- dist/Echo Assistant.app (Application bundle)
- dist/Echo Assistant.dmg (Installer package)

To install:
1. Open Echo Assistant.dmg
2. Drag Echo Assistant to Applications
3. Double-click Echo Assistant in Applications
"