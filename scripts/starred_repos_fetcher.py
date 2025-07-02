#!/usr/bin/env python3
"""
Starred GitHub Repositories Fetcher
Fetches starred repositories from GitHub API and uploads to Google Sheets
"""

import os
import sys
import time
import json
from datetime import datetime
import requests
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv


# === CONFIGURATION ===
load_dotenv()
GHUB_TOKEN = os.getenv('GHUB_TOKEN')
GCP_CREDENTIALS = os.getenv('GCP_CREDENTIALS')
GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

# GitHub API endpoints
API_STARRED_URL = 'https://api.github.com/user/starred'
API_RELEASES_URL = 'https://api.github.com/repos/{owner}/{repo}/releases/latest'
API_TOPICS_URL = 'https://api.github.com/repos/{owner}/{repo}/topics'

auth_headers = {
    'Authorization': f'token {GHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

topics_headers = {
    'Authorization': f'token {GHUB_TOKEN}',
    'Accept': 'application/vnd.github.mercy-preview+json'  # Needed to access topics
}

def get_starred_repos():
    """Fetch all starred repositories from GitHub API"""
    print("🔍 Fetching starred repositories...")
    starred = []
    page = 1

    while True:
        response = requests.get(
            API_STARRED_URL, 
            headers=auth_headers, 
            params={'per_page': 100, 'page': page}
        )
        
        if response.status_code != 200:
            print(f"Error fetching starred repos: {response.status_code} - {response.text}")
            break

        data = response.json()
        if not data:
            break

        starred.extend(data)
        page += 1
        print(f"📦 Fetched page {page-1} ({len(data)} repos)")

    print(f"✅ Total starred repositories: {len(starred)}")
    return starred


def get_last_release_date(owner, repo):
    """Get the last release date for a repository"""
    url = API_RELEASES_URL.format(owner=owner, repo=repo)
    response = requests.get(url, headers=auth_headers)

    if response.status_code == 200:
        return response.json().get("published_at")
    elif response.status_code == 404:
        return "No releases"
    else:
        return f"Error: {response.status_code}"


def get_repo_topics(owner, repo):
    """Get topics for a repository"""
    url = API_TOPICS_URL.format(owner=owner, repo=repo)
    response = requests.get(url, headers=topics_headers)

    if response.status_code == 200:
        return response.json().get('names', [])
    else:
        return []


def process_repositories(repos):
    """Process repositories and gather additional data"""
    print("🔄 Processing repositories and gathering additional data...")
    data = []

    for i, repo in enumerate(repos):
        full_name = repo['full_name']
        owner, repo_name = full_name.split('/')
        
        print(f"📊 Processing {full_name} ({i+1}/{len(repos)})")
        
        # Get additional data
        last_release = get_last_release_date(owner, repo_name)
        topics = get_repo_topics(owner, repo_name)

        data.append({
            'name': full_name,
            'description': repo.get('description', ''),
            'stars': repo['stargazers_count'],
            'forks': repo['forks_count'],
            'language': repo.get('language', 'Unknown'),
            'url': repo['html_url'],
            'last_release': last_release,
            'topics': ", ".join(topics),
            'created_at': repo['created_at'],
            'updated_at': repo['updated_at'],
            'pushed_at': repo.get('pushed_at', ''),
            'open_issues': repo.get('open_issues_count', 0),
            'archived': repo.get('archived', False),
            'fork': repo.get('fork', False),
            'fetched_at': datetime.now().isoformat()
        })

        time.sleep(0.1)

    print(f"✅ Processed {len(data)} repositories")
    return pd.DataFrame(data)


def upload_to_google_sheet(df, sheet_name=GOOGLE_SHEET_NAME):
    """Upload DataFrame to Google Sheets"""
    print(f"📤 Uploading to Google Sheet: {sheet_name}")
    
    # Scope for Sheets + Drive
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        # Load credentials from environment variable (JSON string)
        if GCP_CREDENTIALS.startswith('{'):
            # JSON string
            creds_dict = json.loads(GCP_CREDENTIALS)
        else:
            # File path
            with open(GCP_CREDENTIALS, 'r') as f:
                creds_dict = json.load(f)
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Open (or create) spreadsheet
        try:
            sheet = client.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            sheet = client.create(sheet_name)
            print(f"📝 Created new spreadsheet: {sheet_name}")

        # Use the first worksheet or create it
        worksheet = sheet.worksheet("starred")

        # Clear the sheet and upload new data
        worksheet.clear()
        set_with_dataframe(worksheet, df)
        
        print(f"✅ Uploaded {len(df)} rows to Google Sheet: {sheet_name}")
        print(f"🔗 Sheet URL: https://docs.google.com/spreadsheets/d/{sheet.id}")
        
        return sheet.id
        
    except Exception as e:
        print(f"❌ Error uploading to Google Sheet: {type(e).__name__}: {e.args}")
        raise


def main():
    """Main execution function"""
    print("🚀 Starting starred repositories sync...")
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    
    try:
        # Fetch starred repositories
        repos = get_starred_repos()
        
        if not repos:
            print("⚠️ No starred repositories found")
            return
        
        # Process repositories
        df = process_repositories(repos)
        
        # Upload to Google Sheets
        sheet_id = upload_to_google_sheet(df)
        
        print(f"🎉 Successfully synced {len(df)} starred repositories!")
        print(f"📊 Data available at: https://docs.google.com/spreadsheets/d/{sheet_id}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    
    print(f"✅ Completed at: {datetime.now().isoformat()}")


if __name__ == '__main__':
    main()