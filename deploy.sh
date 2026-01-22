#!/bin/bash

# DOC Deployment Script
# Usage: ./deploy.sh [TESTBED]
# TESTBED: upc, umu, cnit (optional, defaults to upc)

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get testbed argument (default to upc)
TESTBED="${1:-upc}"

# Convert to lowercase
TESTBED=$(echo "$TESTBED" | tr '[:upper:]' '[:lower:]')

# Validate testbed
case "$TESTBED" in
    upc|umu|cnit)
        echo -e "${GREEN}✓ Deploying to testbed: ${TESTBED}${NC}"
        ;;
    *)
        echo -e "${YELLOW}⚠ Invalid testbed '${1}'. Defaulting to 'upc'${NC}"
        TESTBED="upc"
        ;;
esac

# Update CURRENT_TESTBED in .env file
if [ -f .env ]; then
    echo -e "${BLUE}→ Updating .env file with testbed: ${TESTBED}${NC}"
    
    # Check if CURRENT_TESTBED exists in .env
    if grep -q "^CURRENT_TESTBED=" .env; then
        # Update existing line
        sed -i.bak "s/^CURRENT_TESTBED=.*/CURRENT_TESTBED=${TESTBED}/" .env
    else
        # Add it if it doesn't exist
        echo "CURRENT_TESTBED=${TESTBED}" >> .env
    fi
    
    echo -e "${GREEN}✓ .env updated${NC}"
else
    echo -e "${RED}✗ .env file not found!${NC}"
    exit 1
fi

# Update current_domain in config.yaml
if [ -f config/config.yaml ]; then
    echo -e "${BLUE}→ Updating config.yaml with current_domain: ${TESTBED}${NC}"
    
    # Create backup
    cp config/config.yaml config/config.yaml.bak
    
    # Update current_domain in domain_routing section
    sed -i "s/^  current_domain:.*/  current_domain: ${TESTBED}  # Updated by deploy.sh/" config/config.yaml
    
    echo -e "${GREEN}✓ config.yaml updated (backup: config.yaml.bak)${NC}"
else
    echo -e "${YELLOW}⚠ config/config.yaml not found, skipping${NC}"
fi

# Deploy with docker-compose
echo -e "${BLUE}→ Building and starting DOC services...${NC}"
docker-compose up --build -d

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  DOC Deployment Successful! 🚀         ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Testbed:${NC} ${TESTBED}"
    echo -e "${BLUE}API Docs:${NC} http://localhost:$(grep DOC_API_PORT .env | cut -d'=' -f2)/docs"
    echo -e "${BLUE}Health Check:${NC} http://localhost:$(grep DOC_API_PORT .env | cut -d'=' -f2)/ping"
    echo ""
    echo -e "${YELLOW}To view logs:${NC} docker-compose logs -f"
    echo -e "${YELLOW}To stop:${NC} docker-compose down"
    echo ""
else
    echo -e "${RED}✗ Deployment failed${NC}"
    exit 1
fi
