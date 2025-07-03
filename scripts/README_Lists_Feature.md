# GitHub Curated Lists Feature

This feature extends your existing GitHub data pipeline to support curated lists with tags, enabling better organization and analysis of your starred repositories.

## Overview

Instead of just analyzing all starred repositories, this feature allows you to:
- Define curated lists (like "stack", "nice-to-have", "future-ideas") 
- Scrape repositories from multiple lists
- Combine unique repositories with concatenated tags
- Generate focused reports on specific categories

## New Files Created

### Configuration
- **`lists_config.py`** - Central configuration for all your GitHub lists

### Scripts  
- **`starred_lists_fetcher.py`** - Main script that fetches and combines all lists

### Evidence Report Files
- **`sources/github/lists.sql`** - SQL queries for lists data
- **`pages/github/lists.md`** - Evidence report page for curated lists analysis

### Documentation
- **`example_stack_report.md`** - Example markdown report focusing on "stack" tag

## Usage

### 1. Configure Your Lists

Edit `scripts/lists_config.py` to add or modify your GitHub lists:

```python
GITHUB_LISTS = {
    "stack": {
        "url": "https://github.com/stars/Veatec22/lists/stack",
        "description": "Core development stack and essential tools"
    },
    "nice-to-have": {
        "url": "https://github.com/stars/Veatec22/lists/nice-to-have", 
        "description": "Useful tools and libraries for future consideration"
    },
    # Add more lists here...
}
```

### 2. Run the Fetcher

Execute the script to scrape all your lists and upload to Google Sheets:

```bash
cd scripts
python starred_lists_fetcher.py
```

The script will:
- Scrape each list defined in the configuration
- Combine repositories and merge tags for duplicates  
- Upload to a new "lists" tab in your Google Sheet
- Print a summary of repositories and tag distribution

### 3. View Your Evidence Report

The new curated lists data will be available in your Evidence report at `/github/lists`, featuring:

- **Tag Overview**: Distribution of repositories across your tags
- **Stack Focus**: Deep dive into your core development stack
- **Top Repositories**: Most starred tools from your curated lists
- **Cross-Tag Analysis**: Repositories that appear in multiple lists
- **Recent Activity**: Recently updated repositories

## Data Schema

The combined dataset includes these columns:

| Column | Description |
|--------|-------------|
| `name` | Repository full name (owner/repo) |
| `description` | Repository description |
| `stars` | Star count |
| `forks` | Fork count |
| `language` | Primary programming language |
| `url` | GitHub URL |
| `updated_at` | Last updated timestamp |
| `tags` | Comma-separated list of tags |
| `tags_count` | Number of tags for this repository |
| `fetched_at` | When data was last fetched |

## Key Features

### Deduplication
If a repository appears in multiple lists, it will:
- Appear only once in the final dataset
- Have all relevant tags concatenated (e.g., "stack, nice-to-have")
- Use the most recent data if there are conflicts

### Tag-Based Analysis
The Evidence report provides insights like:
- Which tag has the most repositories
- Average stars per tag
- Cross-functional tools (multi-tagged repositories)
- Language distribution by tag

### Automated Reporting
Generate focused reports like the example `example_stack_report.md` which provides:
- Executive summary of your stack
- Technology trends analysis
- Maintenance status overview
- Strategic recommendations

## Integration with Existing Workflow

This feature complements your existing `starred_repos_fetcher.py`:

- **All Starred Repos** (`starred_repos_fetcher.py`) - Comprehensive analysis of everything you've starred
- **Curated Lists** (`starred_lists_fetcher.py`) - Focused analysis of organized, tagged collections

Both datasets live in the same Google Sheet but in different tabs:
- `starred` tab - All starred repositories 
- `lists` tab - Curated lists with tags

## Customization

### Adding New Lists
1. Create the list on GitHub
2. Add it to `lists_config.py`
3. Run the fetcher script

### Modifying Reports  
Edit `pages/github/lists.md` to:
- Add new SQL queries
- Create additional visualizations
- Focus on different aspects of your data

### Scheduling
Consider setting up automated runs (e.g., weekly) to keep your curated lists data fresh:

```bash
# Example cron job (weekly on Sundays at 9 AM)
0 9 * * 0 cd /path/to/scripts && python starred_lists_fetcher.py
```

## Example Output

The `example_stack_report.md` demonstrates a comprehensive analysis focusing on the "stack" tag, including:
- Executive summary with key metrics
- Top repositories by stars
- Language and category breakdowns  
- Cross-tag analysis for versatile tools
- Recent activity and maintenance status
- Technology trends and recommendations

This type of focused analysis helps you understand and communicate your technology choices more effectively.