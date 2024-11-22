#!/bin/bash

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting Noted Backend...${NC}"

# Check if PostgreSQL is running
if ! pgrep -x "postgres" > /dev/null; then
    echo -e "${YELLOW}📦 Starting PostgreSQL service...${NC}"
    sudo systemctl start postgresql
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PostgreSQL service started successfully${NC}"
        # Wait for PostgreSQL to be ready
        sleep 2
        # Create database if it doesn't exist
        if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw noted; then
            echo -e "${YELLOW}🗄️  Creating database 'noted'...${NC}"
            sudo -u postgres createdb noted
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Database 'noted' created successfully${NC}"
            else
                echo -e "${RED}❌ Failed to create database${NC}"
                exit 1
            fi
        fi
    else
        echo -e "${RED}❌ Failed to start PostgreSQL service${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ PostgreSQL service is already running${NC}"
fi

# Check if Redis is running
check_redis_port() {
    local port=$1
    lsof -i :$port > /dev/null 2>&1
    return $?
}

if ! docker ps | grep -q noted-redis; then
    # Check if container exists but is stopped
    if docker ps -a | grep -q noted-redis; then
        echo -e "${YELLOW}📦 Removing stopped Redis container...${NC}"
        docker rm noted-redis
    fi
    
    # Try port 6380 if 6379 is in use
    REDIS_PORT=6380
    
    echo -e "${YELLOW}📦 Starting Redis container on port ${REDIS_PORT}...${NC}"
    docker run -d -p ${REDIS_PORT}:6379 --name noted-redis redis
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Redis container started successfully on port ${REDIS_PORT}${NC}"
    else
        echo -e "${RED}❌ Failed to start Redis container${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Redis container is already running${NC}"
fi

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
cd backend
poetry install
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

# Run migrations
echo -e "${YELLOW}🔄 Running migrations...${NC}"
poetry run python manage.py migrate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migrations completed successfully${NC}"
else
    echo -e "${RED}❌ Failed to run migrations${NC}"
    exit 1
fi

# Start the development server
echo -e "${YELLOW}🌐 Starting development server...${NC}"
poetry run daphne -b 0.0.0.0 -p 8000 core.asgi:application
