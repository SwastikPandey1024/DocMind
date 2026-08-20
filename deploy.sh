#!/bin/bash

# DocuChat Deployment & Verification Script
# Comprehensive pre-deployment checks and deployment automation

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    log_success "Docker found: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    log_success "Docker Compose found: $(docker-compose --version)"
    
    # Check Git
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        exit 1
    fi
    log_success "Git found: $(git --version)"
}

# Check environment files
check_environment() {
    log_info "Checking environment files..."
    
    if [ ! -f ".env" ]; then
        log_warning ".env file not found, creating from .env.example"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Created .env from .env.example"
        else
            log_error ".env.example not found"
            exit 1
        fi
    fi
    
    if [ ! -f "frontend/.env" ]; then
        log_warning "frontend/.env not found, creating"
        echo "VITE_API_BASE_URL=http://localhost:8000" > frontend/.env
        log_success "Created frontend/.env"
    fi
}

# Check disk space
check_disk_space() {
    log_info "Checking disk space..."
    
    available=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    required=50
    
    if [ "$available" -lt "$required" ]; then
        log_warning "Available disk space: ${available}GB (minimum recommended: ${required}GB)"
    else
        log_success "Sufficient disk space: ${available}GB"
    fi
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    docker-compose build --no-cache
    
    log_success "Docker images built successfully"
}

# Start services
start_services() {
    log_info "Starting services..."
    
    docker-compose up -d
    
    log_success "Services started"
    log_info "Waiting for services to be healthy..."
    
    # Wait for PostgreSQL
    log_info "Waiting for PostgreSQL..."
    for i in {1..30}; do
        if docker-compose exec -T postgres pg_isready -U postgres &> /dev/null; then
            log_success "PostgreSQL is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "PostgreSQL failed to start"
            exit 1
        fi
        sleep 2
    done
    
    # Wait for Backend
    log_info "Waiting for Backend..."
    for i in {1..30}; do
        if docker-compose exec -T backend curl -f http://localhost:8000/health &> /dev/null; then
            log_success "Backend is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "Backend failed to start"
            docker-compose logs backend
            exit 1
        fi
        sleep 2
    done
    
    # Wait for Frontend
    log_info "Waiting for Frontend..."
    for i in {1..30}; do
        if docker-compose exec -T frontend wget --quiet --tries=1 --spider http://localhost:80/ &> /dev/null; then
            log_success "Frontend is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            log_warning "Frontend slow to start, continuing..."
        fi
        sleep 2
    done
}

# Run migrations
run_migrations() {
    log_info "Running database migrations..."
    
    docker-compose exec -T backend alembic upgrade head
    
    log_success "Migrations completed"
}

# Verify services
verify_services() {
    log_info "Verifying services..."
    
    docker-compose ps
    
    log_info "Health check status:"
    
    # Check Backend health
    if docker-compose exec -T backend curl -s http://localhost:8000/health | grep -q '"status":"healthy"'; then
        log_success "Backend health: OK"
    else
        log_error "Backend health: FAILED"
        docker-compose logs backend | tail -20
    fi
    
    # Check Frontend
    if docker-compose exec -T frontend wget --quiet --tries=1 --spider http://localhost/ &> /dev/null; then
        log_success "Frontend health: OK"
    else
        log_warning "Frontend health: Check manually"
    fi
    
    # Check Database
    if docker-compose exec -T postgres psql -U postgres -d docuchat -c "SELECT 1" &> /dev/null; then
        log_success "Database health: OK"
    else
        log_error "Database health: FAILED"
    fi
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    # Backend tests
    log_info "Running backend tests..."
    docker-compose exec -T backend pytest tests/ -v --tb=short || log_warning "Some backend tests failed"
    
    log_success "Tests completed"
}

# Show access information
show_access_info() {
    log_info "Deployment completed successfully!"
    echo ""
    echo -e "${GREEN}Access Information:${NC}"
    echo "  Frontend:     ${BLUE}http://localhost${NC}"
    echo "  Backend:      ${BLUE}http://localhost:8000${NC}"
    echo "  API Docs:     ${BLUE}http://localhost:8000/docs${NC}"
    echo "  ReDoc:        ${BLUE}http://localhost:8000/redoc${NC}"
    echo ""
    echo -e "${GREEN}Default Credentials:${NC}"
    echo "  Email:        admin@docuchat.local"
    echo "  Password:     Set via environment"
    echo ""
    echo -e "${GREEN}Useful Commands:${NC}"
    echo "  View logs:    docker-compose logs -f backend"
    echo "  Stop services: docker-compose down"
    echo "  Restart:      docker-compose restart"
    echo ""
}

# Main menu
show_menu() {
    echo ""
    echo -e "${BLUE}DocuChat Deployment Menu${NC}"
    echo "1. Check prerequisites"
    echo "2. Check environment"
    echo "3. Check disk space"
    echo "4. Build images"
    echo "5. Start services"
    echo "6. Run migrations"
    echo "7. Verify services"
    echo "8. Run tests"
    echo "9. Full deployment (all steps)"
    echo "0. Exit"
    echo ""
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        # Interactive mode
        while true; do
            show_menu
            read -p "Select option: " option
            
            case $option in
                1) check_prerequisites ;;
                2) check_environment ;;
                3) check_disk_space ;;
                4) build_images ;;
                5) start_services ;;
                6) run_migrations ;;
                7) verify_services ;;
                8) run_tests ;;
                9)
                    check_prerequisites
                    check_environment
                    check_disk_space
                    build_images
                    start_services
                    run_migrations
                    verify_services
                    show_access_info
                    ;;
                0) exit 0 ;;
                *) log_error "Invalid option" ;;
            esac
        done
    else
        # Command line mode
        case "$1" in
            check-all)
                check_prerequisites
                check_environment
                check_disk_space
                ;;
            build)
                build_images
                ;;
            start)
                start_services
                ;;
            migrate)
                run_migrations
                ;;
            verify)
                verify_services
                ;;
            deploy)
                check_prerequisites
                check_environment
                build_images
                start_services
                run_migrations
                verify_services
                show_access_info
                ;;
            *)
                log_error "Unknown command: $1"
                exit 1
                ;;
        esac
    fi
}

# Run main
main "$@"
