#!/bin/bash
set -e

echo "🧪 Running comprehensive tests..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

TEST_TYPE=${1:-all}

run_backend_tests() {
    echo -e "${BLUE}Running backend tests...${NC}"
    cd backend
    source venv/bin/activate
    
    # Unit tests
    python -m pytest tests/backend/ -v --cov=app --cov-report=html --cov-report=term-missing
    
    # Integration tests
    if [ "$TEST_TYPE" == "all" ] || [ "$TEST_TYPE" == "integration" ]; then
        python -m pytest tests/integration/ -v -m integration
    fi
    
    cd ..
}

run_frontend_tests() {
    echo -e "${BLUE}Running frontend tests...${NC}"
    cd frontend
    npm test -- --coverage --watchAll=false
    cd ..
}

run_lint_tests() {
    echo -e "${BLUE}Running linting...${NC}"
    
    # Backend linting
    cd backend
    source venv/bin/activate
    flake8 app tests --max-line-length=100 --ignore=E203,W503
    mypy app --ignore-missing-imports
    cd ..
    
    # Frontend linting
    cd frontend
    npm run lint
    cd ..
}

run_security_tests() {
    echo -e "${BLUE}Running security tests...${NC}"
    cd backend
    source venv/bin/activate
    bandit -r app -ll
    cd ..
}

run_performance_tests() {
    echo -e "${BLUE}Running performance tests...${NC}"
    # Add performance testing logic here
    echo "Performance tests not implemented yet"
}

# Main test execution
case $TEST_TYPE in
    "unit")
        run_backend_tests
        run_frontend_tests
        ;;
    "integration")
        run_backend_tests
        ;;
    "lint")
        run_lint_tests
        ;;
    "security")
        run_security_tests
        ;;
    "performance")
        run_performance_tests
        ;;
    "all")
        run_lint_tests
        run_security_tests
        run_backend_tests
        run_frontend_tests
        ;;
    *)
        echo "Usage: $0 [unit|integration|lint|security|performance|all]"
        exit 1
        ;;
esac

echo -e "${GREEN}✅ All tests completed successfully!${NC}"