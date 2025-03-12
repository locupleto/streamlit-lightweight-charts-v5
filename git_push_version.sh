#!/bin/bash

# Ensure a version tag is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <version_tag> [commit_message]"
    exit 1
fi

VERSION_TAG="$1"
COMMIT_MESSAGE="${2:-Release $VERSION_TAG}"  # Default message if not provided

# Add all changes
git add .

# Commit changes with the provided or default message
git commit -m "$COMMIT_MESSAGE"

# Tag the commit
git tag "$VERSION_TAG"

# Push changes and tags
git push origin main --tags

echo "Version $VERSION_TAG has been pushed with commit message: '$COMMIT_MESSAGE'."
