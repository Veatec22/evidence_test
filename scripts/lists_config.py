# GitHub Lists Configuration
# This file contains the dictionary of GitHub starred lists to be used as tags

GITHUB_LISTS = {
    "stack": {
        "url": "https://github.com/stars/Veatec22/lists/stack",
        "description": "Core development stack and essential tools"
    },
    "nice-to-have": {
        "url": "https://github.com/stars/Veatec22/lists/nice-to-have", 
        "description": "Useful tools and libraries for future consideration"
    },
    "future-ideas": {
        "url": "https://github.com/stars/Veatec22/lists/future-ideas",
        "description": "Innovative projects and experimental technologies"
    }
}

# List of tag names for easy iteration
TAG_NAMES = list(GITHUB_LISTS.keys())

# Default sheet tab name for the combined lists data
LISTS_SHEET_TAB = "lists"