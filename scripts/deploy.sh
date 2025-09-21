#!/bin/bash
set -e

echo "🚀 Deploying Code Quality Intelligence Agent..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
DEPLOY_ENV=${1:-production}
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"

echo -e "${BLUE}Deploying to: ${DEPLOY_ENV}${NC}"

# Pre-deployment checks
echo -e "${BLUE}Running pre-deployment checks...${NC}"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please configure .env file before proceeding.${NC}"
    exit 1
fi

# Check required environment variables
source .env
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  GEMINI_API_KEY not configured${NC}"
fi

# Run tests
echo -e "${BLUE}Running tests...${NC}"
cd backend && python -m pytest tests/ -x --tb=short
cd ../frontend && npm test -- --coverage --watchAll=false

# Build and deploy
echo -e "${BLUE}Building and deploying...${NC}"
docker-compose -f $DOCKER_COMPOSE_FILE down
docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
docker-compose -f $DOCKER_COMPOSE_FILE up -d

# Health checks
echo -e "${BLUE}Performing health checks...${NC}"
sleep 30  # Wait for services to start

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    exit 1
fi

# Check frontend
if curl -f http://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend may not be ready yet${NC}"
fi

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${BLUE}Access your application at:${NC}"
echo -e "- Frontend: http://localhost"
echo -e "- Backend API: http://localhost:8000"
echo -e "- API Docs: http://localhost:8000/docs"