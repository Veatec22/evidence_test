#!/usr/bin/env python3
"""
Unified Starred GitHub Repositories Fetcher
Fetches starred repositories from GitHub API and merges with curated list tags
Creates a comprehensive portfolio view combining detailed repo data with tag organization
Now uses MotherDuck (cloud DuckDB) for data storage
"""

import os
import sys
import time
import duckdb
from datetime import datetime
from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv

# Import our lists configuration  
from lists_config import GITHUB_LISTS, TAG_NAMES

# === CONFIGURATION ===
load_dotenv()
GHUB_TOKEN = os.getenv('GHUB_TOKEN')
MOTHERDUCK_TOKEN = os.getenv('MOTHERDUCK_TOKEN')
MOTHERDUCK_DB = os.getenv('MOTHERDUCK_DB', 'github')  # Default database name

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

def get_motherduck_connection():
    """Get connection to MotherDuck"""
    try:
        if MOTHERDUCK_TOKEN:
            connection_string = f'md:{MOTHERDUCK_DB}?motherduck_token={MOTHERDUCK_TOKEN}'
        else:
            # Use browser-based authentication
            connection_string = f'md:{MOTHERDUCK_DB}'
        
        conn = duckdb.connect(connection_string)
        print(f"✅ Connected to MotherDuck database: {MOTHERDUCK_DB}")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to MotherDuck: {e}")
        raise

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
    ignore_repos = set()
    
    for tag_name in TAG_NAMES:
        list_config = GITHUB_LISTS[tag_name]
        list_url = list_config['url']
        
        repo_names = scrape_github_list(list_url, tag_name)
        
        if tag_name == 'ignore':
            # Special handling for ignore list
            ignore_repos.update(repo_names)
            print(f"🚫 Added {len(repo_names)} repositories to ignore list")
        else:
            for repo_name in repo_names:
                repo_tags[repo_name].add(tag_name)
        
        # Be nice to GitHub
        time.sleep(1)
    
    print(f"✅ Collected tags for {len(repo_tags)} repositories")
    print(f"🚫 Ignoring {len(ignore_repos)} repositories")
    return repo_tags, ignore_repos

def process_repositories(repos, repo_tags, ignore_repos):
    """Process repositories and gather additional data, merging with curated tags"""
    print("🔄 Processing repositories and gathering additional data...")
    data = []

    for i, repo in enumerate(repos):
        full_name = repo['full_name']
        
        # Skip ignored repositories
        if full_name in ignore_repos:
            print(f"🚫 Skipping ignored repository: {full_name}")
            continue
            
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

    print(f"✅ Processed {len(data)} repositories (filtered out {len([r for r in repos if r['full_name'] in ignore_repos])} ignored)")
    return pd.DataFrame(data)

def upload_to_motherduck(df, table_name="starred"):
    """Upload DataFrame to MotherDuck"""
    print(f"📤 Uploading to MotherDuck: {table_name}")
    
    try:
        conn = get_motherduck_connection()
        
        # Create table if it doesn't exist and insert data
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
        
        # Verify upload
        result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        row_count = result[0]
        
        print(f"✅ Uploaded {row_count} rows to MotherDuck table: {table_name}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error uploading to MotherDuck: {type(e).__name__}: {e}")
        raise

def main():
    """Main execution function"""
    print("🚀 Starting unified starred repositories sync with MotherDuck...")
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    
    try:
        # Fetch starred repositories
        repos = get_starred_repos()
        
        if not repos:
            print("⚠️ No starred repositories found")
            return
        
        # Get curated tags from lists and ignore list
        repo_tags, ignore_repos = get_curated_tags()
        
        # Process repositories with merged data
        df = process_repositories(repos, repo_tags, ignore_repos)
        
        # Upload to MotherDuck
        upload_to_motherduck(df)
        
        # Print summary
        curated_count = len(df[df['is_curated'] == True])
        languages_count = len(df['language'].unique())
        
        print(f"\n📈 Portfolio Summary:")
        print(f"   • Total starred repositories: {len(df)}")
        print(f"   • Curated repositories: {curated_count}")
        print(f"   • Programming languages: {languages_count}")
        print(f"   • Total stars accumulated: {df['stars'].sum():,}")
        print(f"   • Ignored repositories: {len(ignore_repos)}")
        
        # Show curated tag distribution
        if curated_count > 0:
            print(f"   • Curated tag distribution:")
            for tag in [t for t in TAG_NAMES if t != 'ignore']:
                tag_count = len(df[df['curated_tags'].str.contains(tag, na=False)])
                if tag_count > 0:
                    print(f"     - {tag}: {tag_count} repos")
        
        print(f"\n🎉 Successfully synced unified starred repositories to MotherDuck!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    
    print(f"✅ Completed at: {datetime.now().isoformat()}")

if __name__ == '__main__':
    main()