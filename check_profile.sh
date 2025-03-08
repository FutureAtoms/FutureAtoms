#!/bin/bash

# GitHub Profile Health Check Script Runner
# This script runs the profile health checker and displays the results

echo "🚀 GitHub Profile Health Checker"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3 to run this script."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed. Please install pip3 to run this script."
    exit 1
fi

# Install required packages if not already installed
echo "📦 Checking and installing required packages..."
pip3 install --quiet PyGithub requests

# Check if the GitHub token is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️ Warning: GITHUB_TOKEN environment variable is not set."
    echo "Some features of the health check may be limited due to API rate limits."
    echo "To set the token, run: export GITHUB_TOKEN=your_github_token"
    echo ""
    read -p "Do you want to continue without the token? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run the health checker script
echo "🔍 Running profile health check..."
python3 .github/scripts/profile_health_check.py

# Provide guidance on the next steps
echo ""
echo "📋 Next Steps:"
echo "1. Review the recommendations above"
echo "2. Make the suggested improvements to your profile"
echo "3. Commit and push your changes to GitHub"
echo "4. Run this check again to see if all issues are resolved"
echo ""
echo "For more details on maintaining your GitHub profile, refer to PROFILE_MAINTENANCE.md"

# Make the script executable
chmod +x check_profile.sh 