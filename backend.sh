#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if message parameter is provided
if [ -z "$1" ]; then
    echo -e "${BLUE}Please provide a commit message:${NC}"
    read commit_message
else
    commit_message="$1"
fi

echo -e "${GREEN}📦 Processing backend changes...${NC}"

# Navigate to backend directory
cd backend

# Add all changes
git add .

# Commit changes with the provided message
git commit -m "$commit_message"

# Push to the backend branch
git push origin backend

echo -e "${GREEN}✅ Backend changes have been pushed successfully!${NC}"
