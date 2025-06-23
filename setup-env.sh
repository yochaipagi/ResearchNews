#!/bin/bash

# Check if .env file exists
if [ -f .env ]; then
    echo ".env file already exists. Do you want to overwrite it? (y/n)"
    read response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Exiting without changes."
        exit 0
    fi
fi

# Create .env file
cat > .env << EOL
# Database
DATABASE_URL=postgresql://researchfeed:researchfeed@postgres:5432/researchfeed

# Redis
REDIS_URL=redis://redis:6379/0

# LLM Provider
LLM_PROVIDER=gemini

# Google Gemini API
GOOGLE_API_KEY=

# OpenAI (backup/optional)
OPENAI_API_KEY=

# SendGrid
SENDGRID_KEY=

# Web host
WEB_HOST=http://localhost:3000

# Auth
NEXTAUTH_SECRET=$(openssl rand -hex 32)
EOL

echo ".env file created. Please update the GOOGLE_API_KEY in .env with your Gemini API key."
echo "Once done, you can start the application with: docker-compose up -d" 