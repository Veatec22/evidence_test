# GitHub Starred Repositories Setup Guide

This guide will help you set up the automated GitHub starred repositories analysis in your Evidence app.

## Prerequisites

1. **GitHub Personal Access Token** with read access to your starred repositories
2. **Google Service Account** with access to Google Sheets API
3. **Google Sheet** to store the repository data

## Setup Steps

### 1. Create GitHub Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a name like "Evidence Starred Repos"
4. Select the following scopes:
   - `public_repo` (to read public repository information)
   - `user:read` (to read your starred repositories)
5. Generate the token and save it securely

### 2. Create Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it
4. Create a service account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the details and create
5. Generate a JSON key:
   - Click on your service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key" > "JSON"
   - Download the JSON file

### 3. Create Google Sheet

1. Create a new Google Sheet
2. Give it a name (e.g., "StarredRepos")
3. Note the Sheet ID from the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
4. Share the sheet with your service account email (found in the JSON file)
   - Give it "Editor" permissions

### 4. Configure GitHub Repository Secrets

Add the following secrets to your GitHub repository:

1. Go to your repository on GitHub
2. Click "Settings" > "Secrets and variables" > "Actions"
3. Add the following secrets:

#### Required Secrets:
- **`GITHUB_TOKEN`**: Your GitHub personal access token
- **`GOOGLE_CREDENTIALS_JSON`**: The entire contents of your service account JSON file

#### Optional Variables:
- **`GOOGLE_SHEET_NAME`**: Name of your Google Sheet (defaults to "StarredRepos")

### 5. Update Evidence Configuration

1. Update the Google Sheet ID in the Evidence configuration:
   - Edit `sources/github_starred/connection.yaml`
   - Replace `YOUR_GOOGLE_SHEET_ID_HERE` with your actual Sheet ID

2. Add your Google service account credentials to Evidence:
   - In Evidence UI, go to Settings > Data Sources
   - Add a new Google Sheets source named "github_starred"
   - Upload your service account JSON file
   - Set the sheet ID

### 6. Install Dependencies

Run the following commands to install the required dependencies:

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies (if running locally)
pip install -r requirements.txt
```

### 7. Test the Setup

#### Manual Test:
```bash
# Set environment variables
export GITHUB_TOKEN="your_github_token"
export GOOGLE_CREDENTIALS_JSON="path_to_your_json_file_or_json_content"
export GOOGLE_SHEET_NAME="StarredRepos"

# Run the script
python scripts/starred_repos_fetcher.py
```

#### Trigger GitHub Action:
1. Go to your repository on GitHub
2. Click "Actions" tab
3. Find "Sync Starred GitHub Repositories" workflow
4. Click "Run workflow"

## Configuration Options

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GITHUB_TOKEN` | Yes | GitHub personal access token | - |
| `GOOGLE_CREDENTIALS_JSON` | Yes | Google service account JSON | - |
| `GOOGLE_SHEET_NAME` | No | Name of the Google Sheet | StarredRepos |

### Scheduling

The GitHub Action is configured to run daily at 8:00 AM UTC. You can modify the schedule in `.github/workflows/starred-repos-sync.yaml`:

```yaml
on:
  schedule:
    - cron: "0 8 * * *"  # Daily at 8:00 AM UTC
```

## Data Schema

The script collects the following data for each starred repository:

| Field | Description |
|-------|-------------|
| `name` | Repository full name (owner/repo) |
| `description` | Repository description |
| `stars` | Number of stars |
| `forks` | Number of forks |
| `language` | Primary programming language |
| `url` | GitHub URL |
| `last_release` | Last release date or "No releases" |
| `topics` | Repository topics (comma-separated) |
| `created_at` | Repository creation date |
| `updated_at` | Repository last update date |
| `pushed_at` | Last push date |
| `open_issues` | Number of open issues |
| `archived` | Whether the repository is archived |
| `fork` | Whether the repository is a fork |
| `fetched_at` | When the data was fetched |

## Troubleshooting

### Common Issues:

1. **Authentication Error**: Check that your GitHub token has the correct permissions
2. **Google Sheets Access**: Ensure the service account has edit access to your sheet
3. **Rate Limiting**: The script includes delays to respect GitHub API rate limits
4. **Sheet Not Found**: Verify the Google Sheet name and ID are correct

### Logs:
Check the GitHub Actions logs for detailed error information:
1. Go to "Actions" tab in your repository
2. Click on the failed workflow run
3. Expand the "Run starred repos sync" step

## Support

If you encounter issues:
1. Check the GitHub Actions logs
2. Verify all secrets are correctly set
3. Test the Google Sheets connection manually
4. Ensure your GitHub token has the required permissions

---

*This setup creates a fully automated pipeline that updates your Evidence dashboard with fresh repository data daily.*