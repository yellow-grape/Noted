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

# Backend changes
echo -e "${GREEN}📦 Processing backend changes...${NC}"
cd backend
git add .
git commit -m "$commit_message"
git push origin backend

# Frontend changes
echo -e "${GREEN}🎨 Processing frontend changes...${NC}"
cd ../frontend
git add .
git commit -m "$commit_message"
git push origin frontend

# Main project changes
echo -e "${GREEN}📝 Processing main project changes...${NC}"
cd ..
git add .
git commit -m "$commit_message"
git push origin develop

echo -e "${GREEN}✅ All changes have been pushed successfully!${NC}"
