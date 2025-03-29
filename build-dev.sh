#!/bin/bash

# chmod +x build-dev.sh
# build-dev.sh

# Help text
show_help() {
    echo "Usage: build-dev.sh [OPTION]"
    echo "Builds the development environment, including Python virtual environment and frontend assets."
    echo
    echo "Options:"
    echo "  --help            Display this help text and exit"
    echo "  --skip-venv       Skip rebuilding the virtual environment"
    echo
    echo "Examples:"
    echo "  ./build-dev.sh               Rebuild virtual environment and build frontend"
    echo "  ./build-dev.sh --skip-venv   Install dependencies without rebuilding virtual environment"
}

# Function to remove and rebuild the virtual environment
rebuild_virtualenv() {
    echo "Rebuilding virtual environment..."

    # Find and remove the virtual environment folder if it exists
    if [ -d ".venv" ]; then
        deactivate 2>/dev/null
        echo "Removing existing .venv virtual environment..."
        rm -rf .venv
    elif [ -d "venv" ]; then
        deactivate 2>/dev/null
        echo "Removing existing venv virtual environment..."
        rm -rf venv
    fi

    # Create a new virtual environment
    echo "Creating new virtual environment..."
    python -m venv .venv
}

# Parse command-line options
SKIP_VENV=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --help)
            show_help
            exit 0
            ;;
        --skip-venv)
            SKIP_VENV=true
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
    shift
done


# Ensure the script is running in an interactive shell
if [[ $SKIP_VENV == false ]]; then
    if [ -t 0 ]; then
        # Compatibility prompt for both bash and zsh
        echo "Step 1 will remove and rebuild the virtual environment. Are you sure? Type N to install libs only. (y/n)"
        read REPLY
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rebuild_virtualenv
        else
            echo "Skipping virtualenv rebuild, installing libraries only."
        fi
    else
        echo "Running in non-interactive shell, skipping virtualenv rebuild. If you want to rebuild, run ./build-dev.sh"
        echo "Skipping virtualenv rebuild, installing libraries only."
    fi
fi

# Activate the virtual environment
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies if requirements-dev.txt exists
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
fi

# Call various scripts
SERVICE_CONTROL_SCRIPTS_PATH="./service_control/"

CLEAR_CACHE_PATH="${SERVICE_CONTROL_SCRIPTS_PATH}clean_cache.sh"
if [ -f "$CLEAR_CACHE_PATH" ]; then
    echo "Calling clean_cache..."
    bash "$CLEAR_CACHE_PATH"
else
    echo "clean_cache.sh not found at $CLEAR_CACHE_PATH"
    return 1
fi


CLEAR_LOGS_PATH="${SERVICE_CONTROL_SCRIPTS_PATH}clear_logs.sh"
if [ -f "$CLEAR_LOGS_PATH" ]; then
    echo "Calling clear_logs.sh to clear logs..."
    bash "$CLEAR_LOGS_PATH"
else
    echo "clear_logs.sh not found at $CLEAR_LOGS_PATH"
    return 1
fi

echo "Build script completed."
