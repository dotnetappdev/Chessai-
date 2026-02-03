# Build Script for Windows Executable
# This script builds a standalone .exe file with all dependencies

# Install dependencies first if not already installed
# pip install -r requirements.txt

# Build the executable
pyinstaller ChessAI.spec

# The executable will be in the dist/ChessAI/ directory
# It includes all necessary DLLs and dependencies
