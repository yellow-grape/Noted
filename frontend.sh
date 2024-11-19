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

echo -e "${GREEN}🎨 Processing frontend changes...${NC}"

# Navigate to frontend directory
cd frontend

# Add all changes
git add .

# Commit changes with the provided message
git commit -m "$commit_message"

# Push to the frontend branch
git push origin frontend

echo -e "${GREEN}✅ Frontend changes have been pushed successfully!${NC}"
