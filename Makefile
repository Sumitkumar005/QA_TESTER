.PHONY: help install test clean dev prod docker-up docker-down

# Default target
help:
	@echo "Available commands:"
	@echo "  install     Install all dependencies"
	@echo "  test        Run all tests"
	@echo "  clean       Clean up generated files"
	@echo "  dev         Start development servers"
	@echo "  prod        Start production servers"
	@echo "  docker-up   Start with Docker Compose"
	@echo "  docker-down Stop Docker Compose"
	@echo "  lint        Run linters"
	@echo "  format      Format code"

# Installation
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installing test dependencies..."
	cd backend && pip install -r requirements-test.txt
	cd frontend && npm install --save-dev

# Testing
test:
	@echo "Running backend tests..."
	cd backend && pytest tests/ -v --cov=app
	@echo "Running frontend tests..."
	cd frontend && npm test -- --coverage --watchAll=false

test-integration:
	@echo "Running integration tests..."
	cd backend && pytest tests/ -v -m integration

# Development
dev:
	@echo "Starting development servers..."
	@echo "Starting MongoDB..."
	docker run -d --name code-quality-mongo -p 27017:27017 mongo:7.0
	@echo "Starting backend..."
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Starting frontend..."
	cd frontend && npm start

# Production
prod:
	@echo "Building and starting production servers..."
	docker-compose -f docker-compose.prod.yml up -d

# Docker commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

# Code quality
lint:
	@echo "Running backend linting..."
	cd backend && flake8 app tests
	cd backend && mypy app
	@echo "Running frontend linting..."
	cd frontend && npm run lint

format:
	@echo "Formatting backend code..."
	cd backend && black app tests
	@echo "Formatting frontend code..."
	cd frontend && npm run format

# Cleanup
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf backend/htmlcov/
	rm -rf frontend/build/
	rm -rf frontend/coverage/
	docker system prune -f

# Database setup
db-setup:
	@echo "Setting up database..."
	python -c "from app.database.mongodb import init_db; import asyncio; asyncio.run(init_db())"

# CLI testing
cli-test:
	@echo "Testing CLI..."
	cd backend && python -m app.cli health
	cd backend && python -m app.cli languages
