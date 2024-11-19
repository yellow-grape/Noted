#!/bin/bash

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}👋 Stopping Noted Backend...${NC}"

# Kill Django development server
echo -e "${YELLOW}🔍 Finding Django process...${NC}"
DJANGO_PID=$(pgrep -f "python.*manage.py runserver")
if [ ! -z "$DJANGO_PID" ]; then
    echo -e "${YELLOW}🛑 Stopping Django server (PID: $DJANGO_PID)...${NC}"
    kill $DJANGO_PID
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Django server stopped successfully${NC}"
    else
        echo -e "${RED}❌ Failed to stop Django server${NC}"
    fi
else
    echo -e "${GREEN}✅ Django server is not running${NC}"
fi

# Stop Redis service
echo -e "${YELLOW}📦 Stopping Redis service...${NC}"
if pgrep -x "redis-server" > /dev/null; then
    sudo systemctl stop redis
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Redis service stopped successfully${NC}"
    else
        echo -e "${RED}❌ Failed to stop Redis service${NC}"
    fi
else
    echo -e "${GREEN}✅ Redis service is already stopped${NC}"
fi

# Stop PostgreSQL service
echo -e "${YELLOW}🗄️  Stopping PostgreSQL service...${NC}"
if pgrep -x "postgres" > /dev/null; then
    sudo systemctl stop postgresql
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PostgreSQL service stopped successfully${NC}"
    else
        echo -e "${RED}❌ Failed to stop PostgreSQL service${NC}"
    fi
else
    echo -e "${GREEN}✅ PostgreSQL service is already stopped${NC}"
fi

echo -e "${GREEN}✅ All services stopped successfully${NC}"
