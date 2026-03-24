#!/bin/bash

################################################################################
# Presenton Production Health Check Script
# ============================================================================
# Purpose: Verify all services are healthy and operational
# Usage: bash health_check.sh
# Exit Code: 0 if all healthy, 1 if any unhealthy
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Configuration
FASTAPI_URL="http://localhost:8000"
FASTAPI_HEALTH_ENDPOINT="/api/v1/health"
FRONTEND_URL="http://localhost:3000"
NGINX_URL="http://localhost"
METRICS_ENDPOINT="/api/v1/metrics/dashboard"
TIMEOUT=10

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

print_failure() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

################################################################################
# Health Check Functions
################################################################################

check_docker_containers() {
    print_header "Docker Container Status"
    
    # Check if Docker is running
    if ! command -v docker &> /dev/null; then
        print_failure "Docker is not installed"
        return 1
    fi
    
    # Check if Docker daemon is running
    if ! docker ps &> /dev/null; then
        print_failure "Docker daemon is not running"
        return 1
    fi
    
    print_success "Docker daemon is running"
    
    # Check for required containers
    local containers=("presenton-fastapi" "presenton-nextjs" "presenton-nginx")
    
    for container in "${containers[@]}"; do
        if docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
            print_success "Container '$container' is running"
        else
            print_failure "Container '$container' is not running"
            # Try to show why it failed
            if docker ps -a --filter "name=$container" | grep -q "$container"; then
                local status=$(docker ps -a --filter "name=$container" --format "{{.Status}}")
                print_info "Container status: $status"
            fi
        fi
    done
}

check_fastapi_health() {
    print_header "FastAPI Backend Health"
    
    local health_url="${FASTAPI_URL}${FASTAPI_HEALTH_ENDPOINT}"
    
    if curl -sf --max-time $TIMEOUT "$health_url" > /dev/null 2>&1; then
        print_success "FastAPI health endpoint responding"
        
        # Try to get more details
        local response=$(curl -s --max-time $TIMEOUT "$health_url" 2>/dev/null || echo "{}")
        print_info "Response: $response"
    else
        print_failure "FastAPI health endpoint not responding"
        print_info "Tried: $health_url"
        return 1
    fi
}

check_fastapi_connectivity() {
    print_header "FastAPI Connectivity"
    
    # Check if FastAPI is listening on port 8000
    if nc -z localhost 8000 2>/dev/null; then
        print_success "FastAPI port 8000 is open"
    else
        print_failure "FastAPI port 8000 is not responding"
        return 1
    fi
}

check_frontend_health() {
    print_header "Next.js Frontend Health"
    
    if curl -sf --max-time $TIMEOUT "$FRONTEND_URL" > /dev/null 2>&1; then
        print_success "Frontend is responding on port 3000"
    else
        print_failure "Frontend is not responding on port 3000"
        print_info "Tried: $FRONTEND_URL"
        return 1
    fi
}

check_frontend_connectivity() {
    print_header "Frontend Connectivity"
    
    # Check if frontend is listening on port 3000
    if nc -z localhost 3000 2>/dev/null; then
        print_success "Frontend port 3000 is open"
    else
        print_failure "Frontend port 3000 is not responding"
        return 1
    fi
}

check_nginx_proxy() {
    print_header "Nginx Reverse Proxy"
    
    if curl -sf --max-time $TIMEOUT "$NGINX_URL" > /dev/null 2>&1; then
        print_success "Nginx proxy is responding on port 80"
    else
        print_failure "Nginx proxy is not responding on port 80"
        print_info "Tried: $NGINX_URL"
        return 1
    fi
}

check_nginx_connectivity() {
    print_header "Nginx Connectivity"
    
    # Check if nginx is listening on port 80
    if nc -z localhost 80 2>/dev/null; then
        print_success "Nginx port 80 is open"
    else
        print_failure "Nginx port 80 is not responding"
        return 1
    fi
}

check_nginx_config() {
    print_header "Nginx Configuration"
    
    # Check if nginx config file exists
    if [ -f "./nginx.conf" ]; then
        print_success "Nginx configuration file exists"
    else
        print_warning "Nginx configuration file not found at ./nginx.conf"
    fi
}

check_database_connectivity() {
    print_header "Database Connectivity"
    
    # Check if SQLite database file exists
    if [ -f "./app_data/presenton.db" ]; then
        print_success "SQLite database file exists"
        
        # Try to query the database
        if command -v sqlite3 &> /dev/null; then
            if sqlite3 "./app_data/presenton.db" "SELECT 1;" > /dev/null 2>&1; then
                print_success "SQLite database is accessible"
            else
                print_failure "SQLite database is not accessible"
                return 1
            fi
        else
            print_warning "sqlite3 command not found, skipping database query test"
        fi
    else
        print_warning "SQLite database file not found at ./app_data/presenton.db"
        print_info "Database will be created on first run"
    fi
}

check_metrics_endpoint() {
    print_header "Metrics Endpoint"
    
    local metrics_url="${FASTAPI_URL}${METRICS_ENDPOINT}"
    
    if curl -sf --max-time $TIMEOUT "$metrics_url" > /dev/null 2>&1; then
        print_success "Metrics endpoint is responding"
    else
        print_warning "Metrics endpoint is not responding (may not be enabled)"
        print_info "Tried: $metrics_url"
    fi
}

check_api_endpoints() {
    print_header "API Endpoints"
    
    # Check common API endpoints
    local endpoints=(
        "/api/v1/health"
        "/api/v1/presentations"
        "/docs"
        "/openapi.json"
    )
    
    for endpoint in "${endpoints[@]}"; do
        local url="${FASTAPI_URL}${endpoint}"
        if curl -sf --max-time $TIMEOUT "$url" > /dev/null 2>&1; then
            print_success "Endpoint $endpoint is responding"
        else
            print_warning "Endpoint $endpoint is not responding"
        fi
    done
}

check_volumes() {
    print_header "Volume Mounts"
    
    # Check if app_data directory exists
    if [ -d "./app_data" ]; then
        print_success "App data directory exists"
        
        # Check if it's writable
        if [ -w "./app_data" ]; then
            print_success "App data directory is writable"
        else
            print_failure "App data directory is not writable"
            return 1
        fi
    else
        print_warning "App data directory does not exist"
        print_info "Creating app_data directory..."
        mkdir -p ./app_data
        print_success "App data directory created"
    fi
}

check_logs() {
    print_header "Container Logs"
    
    # Check for recent errors in container logs
    local containers=("presenton-fastapi" "presenton-nextjs" "presenton-nginx")
    
    for container in "${containers[@]}"; do
        if docker ps -a --filter "name=$container" | grep -q "$container"; then
            local error_count=$(docker logs "$container" 2>&1 | grep -i "error" | wc -l)
            if [ "$error_count" -gt 0 ]; then
                print_warning "Container '$container' has $error_count error messages in logs"
                print_info "Run: docker logs $container"
            else
                print_success "Container '$container' has no recent errors"
            fi
        fi
    done
}

check_resource_usage() {
    print_header "Resource Usage"
    
    if command -v docker &> /dev/null; then
        local containers=("presenton-fastapi" "presenton-nextjs" "presenton-nginx")
        
        for container in "${containers[@]}"; do
            if docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
                local stats=$(docker stats "$container" --no-stream --format "{{.CPUPerc}} CPU, {{.MemUsage}}")
                print_info "Container '$container': $stats"
            fi
        done
    fi
}

################################################################################
# Summary and Recommendations
################################################################################

print_summary() {
    print_header "Health Check Summary"
    
    echo -e "Passed: ${GREEN}$PASSED${NC}"
    echo -e "Failed: ${RED}$FAILED${NC}"
    echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
    
    if [ $FAILED -eq 0 ]; then
        echo -e "\n${GREEN}✓ All services are healthy!${NC}\n"
        return 0
    else
        echo -e "\n${RED}✗ Some services are unhealthy. See details above.${NC}\n"
        return 1
    fi
}

print_recommendations() {
    print_header "Troubleshooting Recommendations"
    
    if [ $FAILED -gt 0 ]; then
        echo "If services are not running:"
        echo "  1. Start containers: docker-compose -f docker-compose.prod.yml up -d"
        echo "  2. Check logs: docker logs <container-name>"
        echo "  3. Verify .env file is configured correctly"
        echo ""
        echo "If FastAPI is not responding:"
        echo "  1. Check FastAPI logs: docker logs presenton-fastapi"
        echo "  2. Verify database connectivity"
        echo "  3. Check environment variables in .env"
        echo ""
        echo "If Frontend is not responding:"
        echo "  1. Check Next.js logs: docker logs presenton-nextjs"
        echo "  2. Verify port 3000 is not in use"
        echo ""
        echo "If Nginx is not responding:"
        echo "  1. Check Nginx logs: docker logs presenton-nginx"
        echo "  2. Verify nginx.conf is valid"
        echo "  3. Check ports 80 and 443 are not in use"
        echo ""
        echo "For more help:"
        echo "  - Check TROUBLESHOOTING_GUIDE.md"
        echo "  - Review docker-compose.prod.yml configuration"
        echo "  - Verify .env file has all required variables"
    fi
}

################################################################################
# Main Execution
################################################################################

main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║         Presenton Production Health Check                      ║"
    echo "║         $(date '+%Y-%m-%d %H:%M:%S')                                    ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Run all health checks
    check_docker_containers
    check_volumes
    check_nginx_connectivity
    check_nginx_proxy
    check_nginx_config
    check_fastapi_connectivity
    check_fastapi_health
    check_frontend_connectivity
    check_frontend_health
    check_database_connectivity
    check_metrics_endpoint
    check_api_endpoints
    check_logs
    check_resource_usage
    
    # Print summary
    print_summary
    local summary_result=$?
    
    # Print recommendations
    print_recommendations
    
    return $summary_result
}

# Run main function
main
exit $?
