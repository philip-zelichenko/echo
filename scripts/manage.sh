#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Log file paths
LOG_FILE="$HOME/Library/Logs/voiceassistant.log"
ERROR_LOG="$HOME/Library/Logs/voiceassistant.error.log"

# Function to check if service is running
check_status() {
    if pgrep -f "python -m echo.cli start" > /dev/null; then
        echo -e "${GREEN}Voice assistant is running${NC}"
        return 0
    else
        echo -e "${RED}Voice assistant is not running${NC}"
        return 1
    fi
}

# Function to start the service
start_service() {
    echo -e "${YELLOW}Starting voice assistant...${NC}"
    
    # Stop any existing instances
    pkill -f "python -m echo.cli" 2>/dev/null
    sleep 1
    
    # Start the service
    nohup poetry run python -m echo.cli start > "$LOG_FILE" 2> "$ERROR_LOG" &
    
    # Wait a moment and check status
    sleep 2
    check_status
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Voice assistant started successfully${NC}"
        echo -e "${YELLOW}Logs will be written to:${NC}"
        echo -e "  ${YELLOW}Main log: $LOG_FILE${NC}"
        echo -e "  ${YELLOW}Error log: $ERROR_LOG${NC}"
    else
        echo -e "${RED}Failed to start voice assistant${NC}"
        echo -e "${YELLOW}Checking error log...${NC}"
        tail -n 20 "$ERROR_LOG"
    fi
}

# Function to stop the service
stop_service() {
    echo -e "${YELLOW}Stopping voice assistant...${NC}"
    pkill -f "python -m echo.cli"
    sleep 1
    check_status
}

# Function to view logs
view_logs() {
    local log_type=$1
    local lines=${2:-50}  # Default to last 50 lines
    
    case "$log_type" in
        main)
            echo -e "${YELLOW}Last $lines lines of main log:${NC}"
            tail -n "$lines" "$LOG_FILE"
            ;;
        error)
            echo -e "${YELLOW}Last $lines lines of error log:${NC}"
            tail -n "$lines" "$ERROR_LOG"
            ;;
        follow)
            echo -e "${YELLOW}Following main log (Ctrl+C to stop):${NC}"
            tail -f "$LOG_FILE"
            ;;
        *)
            echo -e "${RED}Invalid log type. Use: main, error, or follow${NC}"
            ;;
    esac
}

# Function to clean logs
clean_logs() {
    echo -e "${YELLOW}Cleaning log files...${NC}"
    echo "" > "$LOG_FILE"
    echo "" > "$ERROR_LOG"
    echo -e "${GREEN}Log files cleaned${NC}"
}

# Main logic
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        sleep 1
        start_service
        ;;
    status)
        check_status
        ;;
    logs)
        case "$2" in
            main|error)
                view_logs "$2" "$3"
                ;;
            follow)
                view_logs "follow"
                ;;
            clean)
                clean_logs
                ;;
            *)
                echo "Usage: $0 logs {main|error|follow|clean} [number_of_lines]"
                ;;
        esac
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo "  logs usage: $0 logs {main|error|follow|clean} [number_of_lines]"
        exit 1
esac

exit 0