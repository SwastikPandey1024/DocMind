#!/usr/bin/env bash
# Docker startup and verification script for DocMind

set -e

echo "════════════════════════════════════════════════════════════"
echo "  DocMind Docker Deployment Verification"
echo "════════════════════════════════════════════════════════════"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ docker-compose not found${NC}"
    exit 1
fi

echo ""
echo "Step 1: Validating docker-compose.yml..."
if docker-compose config --quiet 2>/dev/null; then
    echo -e "${GREEN}✓ docker-compose.yml is valid${NC}"
else
    echo -e "${RED}✗ docker-compose.yml has errors${NC}"
    exit 1
fi

echo ""
echo "Step 2: Building images..."
docker-compose build --quiet

echo -e "${GREEN}✓ Images built successfully${NC}"

echo ""
echo "Step 3: Starting services..."
docker-compose up -d

echo -e "${GREEN}✓ Services started${NC}"

echo ""
echo "Step 4: Waiting for services to be healthy..."
sleep 5

RETRIES=30
RETRY_DELAY=2

wait_for_service() {
    local service=$1
    local url=$2
    local attempts=0
    
    echo -n "  Waiting for $service..."
    
    while [ $attempts -lt $RETRIES ]; do
        if docker-compose exec -T $service curl -sf "$url" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        
        attempts=$((attempts + 1))
        sleep $RETRY_DELAY
        echo -n "."
    done
    
    echo -e " ${RED}✗ Timeout${NC}"
    return 1
}

# Wait for PostgreSQL
echo -n "  Waiting for PostgreSQL..."
for i in $(seq 1 $RETRIES); do
    if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    [ $i -lt $RETRIES ] && sleep $RETRY_DELAY && echo -n "."
done

# Wait for Backend
wait_for_service "backend" "http://localhost:8000/health" || {
    echo -e "${YELLOW}⚠ Backend health check failed${NC}"
    echo "Checking logs..."
    docker-compose logs backend | tail -20
    exit 1
}

# Wait for Frontend
wait_for_service "frontend" "http://localhost/" || {
    echo -e "${YELLOW}⚠ Frontend health check failed${NC}"
    echo "Checking logs..."
    docker-compose logs frontend | tail -20
}

echo ""
echo "Step 5: Running database migrations..."
docker-compose exec -T backend alembic upgrade head

echo -e "${GREEN}✓ Migrations completed${NC}"

echo ""
echo "Step 6: Service Health Check"
echo ""
docker-compose ps
echo ""

echo "Step 7: Connectivity Tests"
echo ""

echo -n "  Backend: "
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
fi

echo -n "  Frontend: "
if curl -sf http://localhost/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
fi

echo -n "  Database: "
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
fi

echo -n "  Ollama: "
if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${YELLOW}⚠ Not responding (optional)${NC}"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ DocMind is running!${NC}"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Access URLs:"
echo "  Frontend: http://localhost"
echo "  API Docs: http://localhost:8000/docs"
echo "  API (ReDoc): http://localhost:8000/redoc"
echo ""
echo "Database credentials:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: docmind"
echo "  User: postgres"
echo ""
echo "View logs:"
echo "  docker-compose logs -f backend"
echo "  docker-compose logs -f frontend"
echo ""
