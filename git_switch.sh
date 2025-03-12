#!/bin/bash

# Function to display help
show_help() {
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  list        - Lists all available tags (versions)"
    echo "  <tag_name>  - Switches to the specified tag in detached mode"
    echo "  back        - Returns to the latest commit on the main branch"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 v1.02"
    echo "  $0 back"
    exit 0
}

# Check if an argument is provided
if [ -z "$1" ]; then
    show_help
fi

case "$1" in
    list)
        git tag -n
        ;;
    back)
        git switch main || git checkout main
        echo "Switched back to the latest commit on main."
        ;;
    -h|--help|?)
        show_help
        ;;
    *)
        git switch --detach "$1" 2>/dev/null || git checkout "$1"
        echo "Switched to tag $1 in detached HEAD mode."
        ;;
esac
