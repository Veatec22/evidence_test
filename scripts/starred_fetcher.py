#!/usr/bin/env python3
"""
Unified Starred GitHub Repositories Fetcher
Fetches starred repositories from GitHub API and merges with curated list tags
Creates a comprehensive portfolio view combining detailed repo data with tag organization
"""

import os
import sys
import time
import json
from datetime import datetime
from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# Import our lists configuration  
from lists_config import GITHUB_LISTS, TAG_NAMES

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

def scrape_github_list(list_url, tag_name):
    """Scrape a single GitHub list and return repository names with tag"""
    print(f"🔍 Scraping list '{tag_name}': {list_url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(list_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to load page for {tag_name}: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        repo_blocks = soup.select('div#user-list-repositories > div.border-bottom')

        repo_names = []
        for block in repo_blocks:
            name_tag = block.select_one('h3 a')
            if not name_tag:
                continue
                
            full_name = name_tag['href'].strip('/')
            repo_names.append(full_name)

        print(f"✅ Found {len(repo_names)} repositories in '{tag_name}' list")
        return repo_names
        
    except Exception as e:
        print(f"❌ Error scraping {tag_name}: {str(e)}")
        return []

def get_curated_tags():
    """Fetch all curated lists and create a mapping of repo names to tags"""
    print("🏷️ Fetching curated list tags...")
    repo_tags = defaultdict(set)
    
    for tag_name in TAG_NAMES:
        list_config = GITHUB_LISTS[tag_name]
        list_url = list_config['url']
        
        repo_names = scrape_github_list(list_url, tag_name)
        for repo_name in repo_names:
            repo_tags[repo_name].add(tag_name)
        
        # Be nice to GitHub
        time.sleep(1)
    
    print(f"✅ Collected tags for {len(repo_tags)} repositories")
    return repo_tags

def process_repositories(repos, repo_tags):
    """Process repositories and gather additional data, merging with curated tags"""
    print("🔄 Processing repositories and gathering additional data...")
    data = []

    for i, repo in enumerate(repos):
        full_name = repo['full_name']
        owner, repo_name = full_name.split('/')
        
        print(f"📊 Processing {full_name} ({i+1}/{len(repos)})")
        
        # Get additional data
        last_release = get_last_release_date(owner, repo_name)
        topics = get_repo_topics(owner, repo_name)
        
        # Get curated tags for this repo
        curated_tags = list(repo_tags.get(full_name, set()))
        
        # Combine GitHub topics and curated tags
        all_tags = topics + curated_tags
        
        data.append({
            'name': full_name,
            'description': repo.get('description', ''),
            'stars': repo['stargazers_count'],
            'forks': repo['forks_count'],
            'language': repo.get('language', 'Unknown'),
            'url': repo['html_url'],
            'last_release': last_release,
            'topics': ", ".join(topics),
            'curated_tags': ", ".join(sorted(curated_tags)),
            'all_tags': ", ".join(sorted(all_tags)),
            'tags_count': len(all_tags),
            'is_curated': len(curated_tags) > 0,
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

def upload_to_google_sheet(df, sheet_name=GOOGLE_SHEET_NAME, tab_name="starred"):
    """Upload DataFrame to Google Sheets"""
    print(f"📤 Uploading to Google Sheet: {sheet_name}, tab: {tab_name}")
    
    # Scope for Sheets + Drive
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        # Validate credentials
        if not GCP_CREDENTIALS:
            raise ValueError("GCP_CREDENTIALS environment variable is not set")
        
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

        # Try to get the worksheet, create if it doesn't exist
        try:
            worksheet = sheet.worksheet(tab_name)
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=tab_name, rows="1000", cols="25")
            print(f"📝 Created new worksheet: {tab_name}")

        # Clear the sheet and upload new data
        worksheet.clear()
        set_with_dataframe(worksheet, df)
        
        print(f"✅ Uploaded {len(df)} rows to Google Sheet: {sheet_name}/{tab_name}")
        print(f"🔗 Sheet URL: https://docs.google.com/spreadsheets/d/{sheet.id}")
        
        return sheet.id
        
    except Exception as e:
        print(f"❌ Error uploading to Google Sheet: {type(e).__name__}: {e}")
        raise

def main():
    """Main execution function"""
    print("🚀 Starting unified starred repositories sync...")
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    
    try:
        # Fetch starred repositories
        repos = get_starred_repos()
        
        if not repos:
            print("⚠️ No starred repositories found")
            return
        
        # Get curated tags from lists
        repo_tags = get_curated_tags()
        
        # Process repositories with merged data
        df = process_repositories(repos, repo_tags)
        
        # Upload to Google Sheets
        sheet_id = upload_to_google_sheet(df)
        
        # Print summary
        curated_count = len(df[df['is_curated'] == True])
        languages_count = len(df['language'].unique())
        
        print(f"\n📈 Portfolio Summary:")
        print(f"   • Total starred repositories: {len(df)}")
        print(f"   • Curated repositories: {curated_count}")
        print(f"   • Programming languages: {languages_count}")
        print(f"   • Total stars accumulated: {df['stars'].sum():,}")
        
        # Show curated tag distribution
        if curated_count > 0:
            print(f"   • Curated tag distribution:")
            for tag in TAG_NAMES:
                tag_count = len(df[df['curated_tags'].str.contains(tag, na=False)])
                if tag_count > 0:
                    print(f"     - {tag}: {tag_count} repos")
        
        print(f"\n🎉 Successfully synced unified starred repositories!")
        print(f"📊 Portfolio data available at: https://docs.google.com/spreadsheets/d/{sheet_id}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    
    print(f"✅ Completed at: {datetime.now().isoformat()}")

if __name__ == '__main__':
    main()