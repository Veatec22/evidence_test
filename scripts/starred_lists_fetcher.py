#!/usr/bin/env python3
"""
GitHub Starred Lists Fetcher with Tags
Fetches repositories from multiple GitHub starred lists and combines them with tags
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
from lists_config import GITHUB_LISTS, TAG_NAMES, LISTS_SHEET_TAB

# === CONFIGURATION ===
load_dotenv()
GCP_CREDENTIALS = os.getenv('GCP_CREDENTIALS')
GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

def scrape_github_list(list_url, tag_name):
    """Scrape a single GitHub list and return repository data with tag"""
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

        data = []
        for block in repo_blocks:
            name_tag = block.select_one('h3 a')
            if not name_tag:
                continue
                
            full_name = name_tag['href'].strip('/')
            repo_url = f"https://github.com/{full_name}"

            desc_tag = block.select_one('[itemprop=description]')
            description = desc_tag.text.strip() if desc_tag else ''

            lang_tag = block.select_one('[itemprop=programmingLanguage]')
            language = lang_tag.text.strip() if lang_tag else ''

            stars_tag = block.select_one('a[href$="/stargazers"]')
            stars_text = stars_tag.get_text().strip().replace(',', '') if stars_tag else '0'
            
            forks_tag = block.select_one('a[href$="/forks"]')
            forks_text = forks_tag.get_text().strip().replace(',', '') if forks_tag else '0'

            updated_tag = block.select_one('relative-time')
            updated = updated_tag['datetime'] if updated_tag else ''

            # Parse stars and forks (handle 'k' suffix)
            stars = parse_number_with_suffix(stars_text)
            forks = parse_number_with_suffix(forks_text)

            data.append({
                'name': full_name,
                'url': repo_url,
                'description': description,
                'language': language,
                'stars': stars,
                'forks': forks,
                'updated_at': updated,
                'tag': tag_name
            })

        print(f"✅ Found {len(data)} repositories in '{tag_name}' list")
        return data
        
    except Exception as e:
        print(f"❌ Error scraping {tag_name}: {str(e)}")
        return []

def parse_number_with_suffix(text):
    """Parse numbers that might have 'k' suffix (e.g., '1.2k' -> 1200)"""
    if not text or text == '0':
        return 0
    
    text = text.lower().strip()
    if text.endswith('k'):
        try:
            return int(float(text[:-1]) * 1000)
        except ValueError:
            return 0
    
    try:
        return int(text)
    except ValueError:
        return 0

def combine_repos_with_tags(all_repos_data):
    """Combine repositories from multiple lists and concatenate tags"""
    print("🔄 Combining repositories and merging tags...")
    
    # Group repos by name (full_name)
    repo_dict = {}
    
    # Process all repos and collect tags
    for repo_data in all_repos_data:
        repo_name = repo_data['name']
        tag = repo_data['tag']
        
        # Initialize repo entry if not exists
        if repo_name not in repo_dict:
            repo_dict[repo_name] = {
                'tags': set(),
                'data': None
            }
        
        # Add tag to this repo
        repo_dict[repo_name]['tags'].add(tag)
        
        # Store repo data (use the first occurrence or update with more recent)
        if repo_dict[repo_name]['data'] is None:
            repo_dict[repo_name]['data'] = repo_data.copy()
            del repo_dict[repo_name]['data']['tag']  # Remove individual tag
        else:
            # Update with more recent data if available
            existing = repo_dict[repo_name]['data']
            if repo_data.get('updated_at') and existing.get('updated_at'):
                if repo_data['updated_at'] > existing['updated_at']:
                    repo_dict[repo_name]['data'] = repo_data.copy()
                    del repo_dict[repo_name]['data']['tag']
    
    # Create final combined list
    combined_data = []
    for repo_name, repo_info in repo_dict.items():
        repo_data = repo_info['data']
        tags_list = sorted(list(repo_info['tags']))
        
        repo_data['tags'] = ', '.join(tags_list)
        repo_data['tags_count'] = len(tags_list)
        repo_data['fetched_at'] = datetime.now().isoformat()
        
        combined_data.append(repo_data)
    
    print(f"✅ Combined {len(combined_data)} unique repositories with tags")
    
    # Sort by stars descending
    combined_data.sort(key=lambda x: x.get('stars', 0), reverse=True)
    
    return pd.DataFrame(combined_data)

def fetch_all_lists():
    """Fetch repositories from all configured GitHub lists"""
    print("🚀 Starting to fetch all GitHub lists...")
    print(f"📋 Lists to process: {', '.join(TAG_NAMES)}")
    
    all_repos = []
    
    for tag_name in TAG_NAMES:
        list_config = GITHUB_LISTS[tag_name]
        list_url = list_config['url']
        
        repos = scrape_github_list(list_url, tag_name)
        all_repos.extend(repos)
        
        # Be nice to GitHub
        time.sleep(1)
    
    print(f"📊 Total repositories fetched: {len(all_repos)}")
    
    # Combine and process
    if all_repos:
        return combine_repos_with_tags(all_repos)
    else:
        print("⚠️ No repositories found in any list")
        return pd.DataFrame()

def upload_to_google_sheet(df, sheet_name=GOOGLE_SHEET_NAME, tab_name=LISTS_SHEET_TAB):
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
            worksheet = sheet.add_worksheet(title=tab_name, rows="1000", cols="20")
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
    print("🚀 Starting GitHub starred lists sync with tags...")
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    
    try:
        # Fetch all lists
        df = fetch_all_lists()
        
        if df.empty:
            print("⚠️ No repositories found in any list")
            return
        
        # Upload to Google Sheets
        sheet_id = upload_to_google_sheet(df)
        
        # Print summary
        print(f"\n📈 Summary:")
        print(f"   • Total unique repositories: {len(df)}")
        print(f"   • Lists processed: {', '.join(TAG_NAMES)}")
        
        # Show tag distribution
        tag_counts = {}
        for _, row in df.iterrows():
            for tag in row['tags'].split(', '):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        print(f"   • Tag distribution:")
        for tag, count in sorted(tag_counts.items()):
            print(f"     - {tag}: {count} repos")
        
        print(f"\n🎉 Successfully synced GitHub lists!")
        print(f"📊 Data available at: https://docs.google.com/spreadsheets/d/{sheet_id}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    
    print(f"✅ Completed at: {datetime.now().isoformat()}")

if __name__ == '__main__':
    main()