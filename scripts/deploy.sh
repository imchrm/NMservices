#!/bin/bash

# NMservices Deployment Helper Script
# Helps deploy and manage the service on remote server

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
REMOTE_HOST="${REMOTE_HOST:-12.34.56.78}"
REMOTE_PORT="${REMOTE_PORT:-2251}"
REMOTE_USER="${REMOTE_USER:-}"
SERVICE_PORT="${SERVICE_PORT:-9800}"
PROJECT_DIR="${PROJECT_DIR:-~/projects/NMservices}"

# Usage
usage() {
    cat << EOF
Usage: $0 <command> [OPTIONS]

Deployment helper for NMservices.

COMMANDS:
    connect             Connect to remote server via SSH
    deploy              Deploy application to remote server
    status              Check service status
    logs                Show service logs
    stop                Stop the service
    restart             Restart the service
    test                Test remote API
    help                Show this help

OPTIONS:
    -u, --user USER     Remote username
    -h, --host HOST     Remote host (default: $REMOTE_HOST)
    -p, --port PORT     SSH port (default: $REMOTE_PORT)
    -s, --service PORT  Service port (default: $SERVICE_PORT)

ENVIRONMENT VARIABLES:
    REMOTE_USER         Remote username
    REMOTE_HOST         Remote host
    REMOTE_PORT         SSH port
    SERVICE_PORT        Service port
    API_KEY             API key for testing

EXAMPLES:
    # Connect to server
    $0 connect -u myuser

    # Deploy service
    $0 deploy -u myuser

    # Check status
    $0 status -u myuser

    # View logs
    $0 logs -u myuser

    # Test API
    API_KEY=secret123 $0 test -u myuser

EOF
    exit 0
}

# Parse arguments
COMMAND=""
while [[ $# -gt 0 ]]; do
    case $1 in
        connect|deploy|status|logs|stop|restart|test|help)
            COMMAND="$1"
            shift
            ;;
        -u|--user)
            REMOTE_USER="$2"
            shift 2
            ;;
        -h|--host)
            REMOTE_HOST="$2"
            shift 2
            ;;
        -p|--port)
            REMOTE_PORT="$2"
            shift 2
            ;;
        -s|--service)
            SERVICE_PORT="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            usage
            ;;
    esac
done

# Check if user is provided
if [ -z "$REMOTE_USER" ] && [ "$COMMAND" != "help" ]; then
    echo -e "${RED}Error: Remote username is required${NC}"
    echo "Use -u option or set REMOTE_USER environment variable"
    exit 1
fi

# SSH command builder
ssh_cmd() {
    ssh -p "$REMOTE_PORT" "${REMOTE_USER}@${REMOTE_HOST}" "$@"
}

# Command: connect
cmd_connect() {
    echo -e "${BLUE}Connecting to ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PORT}${NC}"
    ssh -p "$REMOTE_PORT" "${REMOTE_USER}@${REMOTE_HOST}"
}

# Command: deploy
cmd_deploy() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Deploying NMservices${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    echo -e "${YELLOW}1. Checking remote environment...${NC}"
    ssh_cmd "which python3 && which git && which poetry" || {
        echo -e "${RED}Error: Required tools not found on remote server${NC}"
        echo "Please install: python3, git, poetry"
        exit 1
    }

    echo -e "${GREEN}✓ Remote environment OK${NC}"
    echo ""

    echo -e "${YELLOW}2. Checking if project exists...${NC}"
    if ssh_cmd "[ -d $PROJECT_DIR ]"; then
        echo -e "${YELLOW}Project exists, updating...${NC}"
        ssh_cmd "cd $PROJECT_DIR && git pull origin main"
    else
        echo -e "${YELLOW}Cloning project...${NC}"
        ssh_cmd "mkdir -p ~/projects && cd ~/projects && git clone https://github.com/imchrm/NMservices.git"
    fi

    echo -e "${GREEN}✓ Project code updated${NC}"
    echo ""

    echo -e "${YELLOW}3. Installing dependencies...${NC}"
    ssh_cmd "cd $PROJECT_DIR && poetry install --no-dev"
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    echo ""

    echo -e "${YELLOW}4. Checking .env file...${NC}"
    if ssh_cmd "[ -f $PROJECT_DIR/.env ]"; then
        echo -e "${GREEN}✓ .env file exists${NC}"
    else
        echo -e "${YELLOW}Creating .env file...${NC}"
        ssh_cmd "cd $PROJECT_DIR && cat > .env << 'EOF'
API_SECRET_KEY=\$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
HOST=0.0.0.0
PORT=$SERVICE_PORT
ENVIRONMENT=production
EOF"
        echo -e "${GREEN}✓ .env file created${NC}"
    fi
    echo ""

    echo -e "${YELLOW}5. Starting service...${NC}"
    ssh_cmd "cd $PROJECT_DIR && pkill -f 'uvicorn nms.main' || true"
    ssh_cmd "cd $PROJECT_DIR && nohup poetry run uvicorn nms.main:app --host 0.0.0.0 --port $SERVICE_PORT > ~/nms.log 2>&1 & echo \$! > ~/nms.pid"

    sleep 2

    if ssh_cmd "ps -p \$(cat ~/nms.pid) > /dev/null 2>&1"; then
        echo -e "${GREEN}✓ Service started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start service${NC}"
        exit 1
    fi
    echo ""

    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}Deployment completed!${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Service URL: http://${REMOTE_HOST}:${SERVICE_PORT}"
    echo ""
    echo "Next steps:"
    echo "  1. Test: $0 test -u $REMOTE_USER"
    echo "  2. Logs: $0 logs -u $REMOTE_USER"
    echo "  3. Status: $0 status -u $REMOTE_USER"
}

# Command: status
cmd_status() {
    echo -e "${BLUE}Checking service status...${NC}"
    echo ""

    echo -e "${YELLOW}Process status:${NC}"
    if ssh_cmd "[ -f ~/nms.pid ] && ps -p \$(cat ~/nms.pid) > /dev/null 2>&1"; then
        ssh_cmd "ps -p \$(cat ~/nms.pid) -o pid,user,%cpu,%mem,cmd"
        echo -e "${GREEN}✓ Service is running${NC}"
    else
        echo -e "${RED}✗ Service is not running${NC}"
        exit 1
    fi
    echo ""

    echo -e "${YELLOW}Port status:${NC}"
    ssh_cmd "ss -tuln | grep $SERVICE_PORT"
    echo ""

    echo -e "${YELLOW}Recent logs:${NC}"
    ssh_cmd "tail -5 ~/nms.log"
}

# Command: logs
cmd_logs() {
    echo -e "${BLUE}Showing service logs (Ctrl+C to stop)...${NC}"
    echo ""
    ssh_cmd "tail -f ~/nms.log"
}

# Command: stop
cmd_stop() {
    echo -e "${YELLOW}Stopping service...${NC}"

    if ssh_cmd "[ -f ~/nms.pid ]"; then
        ssh_cmd "kill \$(cat ~/nms.pid) && rm ~/nms.pid"
        echo -e "${GREEN}✓ Service stopped${NC}"
    else
        echo -e "${YELLOW}No PID file found, trying to kill by name...${NC}"
        ssh_cmd "pkill -f 'uvicorn nms.main' || true"
        echo -e "${GREEN}✓ Done${NC}"
    fi
}

# Command: restart
cmd_restart() {
    echo -e "${BLUE}Restarting service...${NC}"
    cmd_stop
    sleep 2

    echo -e "${YELLOW}Starting service...${NC}"
    ssh_cmd "cd $PROJECT_DIR && nohup poetry run uvicorn nms.main:app --host 0.0.0.0 --port $SERVICE_PORT > ~/nms.log 2>&1 & echo \$! > ~/nms.pid"

    sleep 2

    if ssh_cmd "ps -p \$(cat ~/nms.pid) > /dev/null 2>&1"; then
        echo -e "${GREEN}✓ Service restarted successfully${NC}"
    else
        echo -e "${RED}✗ Failed to restart service${NC}"
        exit 1
    fi
}

# Command: test
cmd_test() {
    echo -e "${BLUE}Testing remote API...${NC}"
    echo ""

    if [ -z "$API_KEY" ]; then
        echo -e "${YELLOW}Warning: API_KEY not set, using default${NC}"
        API_KEY="test_secret"
    fi

    # Run local test script
    if [ -f "scripts/test_api.sh" ]; then
        ./scripts/test_api.sh \
            --host "$REMOTE_HOST" \
            --port "$SERVICE_PORT" \
            --key "$API_KEY"
    else
        echo -e "${RED}Error: test_api.sh not found${NC}"
        echo "Make sure you're in the project root directory"
        exit 1
    fi
}

# Main execution
case "$COMMAND" in
    connect)
        cmd_connect
        ;;
    deploy)
        cmd_deploy
        ;;
    status)
        cmd_status
        ;;
    logs)
        cmd_logs
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    test)
        cmd_test
        ;;
    help|"")
        usage
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$COMMAND'${NC}"
        usage
        ;;
esac
