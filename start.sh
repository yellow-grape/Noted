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
if ! pgrep -x "redis-server" > /dev/null; then
    echo -e "${YELLOW}📦 Starting Redis service...${NC}"
    sudo systemctl start redis
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Redis service started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start Redis service${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Redis service is already running${NC}"
fi

# Change to the backend directory
cd backend

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Poetry is not installed. Please install it first:${NC}"
    echo "curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Run migrations
echo -e "${YELLOW}🔄 Running database migrations...${NC}"
poetry run python manage.py migrate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migrations completed successfully${NC}"
else
    echo -e "${RED}❌ Migration failed${NC}"
    exit 1
fi

# Start the Django development server
echo -e "${YELLOW}🌐 Starting Django development server...${NC}"
poetry run python manage.py runserver &
DJANGO_PID=$!

# Start the ASGI server for WebSocket support
echo -e "${YELLOW}🔌 Starting ASGI server for WebSocket support...${NC}"
DJANGO_SETTINGS_MODULE=core.settings poetry run daphne -b 0.0.0.0 -p 8001 core.asgi:application &
ASGI_PID=$!

# Trap Ctrl+C and cleanup
trap 'echo -e "${YELLOW}\n👋 Shutting down...${NC}"; kill $DJANGO_PID; kill $ASGI_PID; exit 0' INT

# Wait for both servers
wait
