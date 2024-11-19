#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if message parameter is provided
if [ -z "$1" ]; then
    echo -e "${BLUE}Please provide a commit message:${NC}"
    read commit_message
else
    commit_message="$1"
fi

echo -e "${YELLOW}🚀 Processing all changes...${NC}"

# Add all changes
git add .

# Commit changes with the provided message
git commit -m "$commit_message"

# Push to develop branch
git push origin develop

echo -e "${GREEN}✅ All changes have been pushed successfully!${NC}"
