#!/usr/bin/env python3
"""
Unified GitHub Repository Sync
Combines starred repository fetching and recommendation generation
Simplified: no descriptions, only essential fields
"""

import os
import sys
import time
import duckdb
import requests
import pandas as pd
from datetime import datetime
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tqdm import tqdm

# GitHub Lists (slug-only format)
GITHUB_LISTS = [
    "future-ideas",
    "stack",
    "nice-to-have",
    "ignore",
    "education",
]

GITHUB_LISTS_ADDITIONAL = [
    "ds-ml-frameworks",
    "llm-context-scraping",
    "bi-data",
    "mlops-pipelines",
    "ux-ui-creative-tools",
    "project-management",
    "de-performance"
]

load_dotenv()
GHUB_TOKEN = os.getenv('GHUB_TOKEN')
MOTHERDUCK_TOKEN = os.getenv('MOTHERDUCK_TOKEN')
MOTHERDUCK_DB = os.getenv('MOTHERDUCK_DB', 'github')

BASE_LIST_URL = "https://github.com/stars/Veatec22/lists/"

auth_headers = {
    'Authorization': f'token {GHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

topics_headers = {
    'Authorization': f'token {GHUB_TOKEN}',
    'Accept': 'application/vnd.github.mercy-preview+json'
}

def get_motherduck_connection():
    try:
        conn_str = f"md:{MOTHERDUCK_DB}"
        if MOTHERDUCK_TOKEN:
            conn_str += f"?motherduck_token={MOTHERDUCK_TOKEN}"
        return duckdb.connect(conn_str)
    except Exception as e:
        print(f"❌ Error connecting to MotherDuck: {e}")
        raise

def get_starred_repos():
    starred = []
    page = 1
    with tqdm(desc="Fetching starred repos", unit="pages") as pbar:
        while True:
            resp = requests.get(
                'https://api.github.com/user/starred',
                headers=auth_headers,
                params={'per_page': 100, 'page': page}
            )
            if resp.status_code != 200:
                print(f"Error fetching starred repos: {resp.status_code}")
                break
            data = resp.json()
            if not data:
                break
            starred.extend(data)
            page += 1
            pbar.update(1)
            pbar.set_postfix(total=len(starred))
    return starred

def scrape_github_list(slug):
    url = BASE_LIST_URL + slug
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        blocks = soup.select('div#user-list-repositories > div.border-bottom')
        return [a['href'].strip('/') for b in blocks if (a := b.select_one('h3 a'))]
    except Exception as e:
        print(f"❌ Error scraping {slug}: {str(e)}")
        return []

def get_curated_tags():
    repo_tags = defaultdict(set)
    ignore_repos = set()
    for slug in tqdm(GITHUB_LISTS, desc="Fetching curated lists"):
        repos = scrape_github_list(slug)
        if slug == "ignore":
            ignore_repos.update(repos)
        else:
            for r in repos:
                repo_tags[r].add(slug)
        time.sleep(1)
    return repo_tags, ignore_repos

def get_last_release_date(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/releases/latest'
    resp = requests.get(url, headers=auth_headers)
    if resp.status_code == 200:
        return resp.json().get("published_at")
    elif resp.status_code == 404:
        return "No releases"
    return f"Error: {resp.status_code}"

def get_repo_topics(owner, repo):
    url = f'https://api.github.com/repos/{owner}/{repo}/topics'
    resp = requests.get(url, headers=topics_headers)
    return resp.json().get('names', []) if resp.status_code == 200 else []

def process_starred_repositories(repos, repo_tags, ignore_repos):
    data = []
    for repo in tqdm(repos, desc="Processing starred repos"):
        full_name = repo['full_name']
        if full_name in ignore_repos:
            continue
        owner, repo_name = full_name.split('/')
        last_release = get_last_release_date(owner, repo_name)
        topics = get_repo_topics(owner, repo_name)
        curated_tags = list(repo_tags.get(full_name, set()))
        all_tags = topics + curated_tags
        data.append({
            'name': full_name,
            'stars': repo['stargazers_count'],
            'language': repo.get('language', 'Unknown'),
            'url': repo['html_url'],
            'last_release': last_release,
            'curated_tags': ", ".join(sorted(curated_tags)),
            'all_tags': ", ".join(sorted(all_tags)),
            'is_curated': len(curated_tags) > 0
        })
        time.sleep(0.1)
    return pd.DataFrame(data)

def generate_recommendations(starred_df, ignore_repos, min_stars=1000, max_per_topic=50):
    all_topics = []
    starred_names = set(starred_df['name'])
    for tags in starred_df['all_tags']:
        all_topics.extend([t.strip().lower() for t in tags.split(',') if t.strip()])
    topic_counter = Counter(all_topics)
    if not topic_counter:
        return pd.DataFrame()

    recommendations = {}
    for topic, _ in tqdm(topic_counter.most_common(), desc="Searching topics"):
        params = {
            'q': f"topic:{topic} stars:>={min_stars}",
            'sort': 'stars',
            'order': 'desc',
            'per_page': min(max_per_topic, 100),
            'page': 1
        }
        try:
            resp = requests.get('https://api.github.com/search/repositories', headers=auth_headers, params=params)
            if resp.status_code != 200:
                continue
            for repo in resp.json().get('items', []):
                if repo['full_name'] in starred_names or repo['full_name'] in ignore_repos:
                    continue
                recommendations[repo['id']] = {
                    'name': repo['full_name'],
                    'stars': repo['stargazers_count'],
                    'language': repo.get('language', 'Unknown'),
                    'url': repo['html_url']
                }
            time.sleep(0.1)
        except Exception as e:
            print(f"❌ Error searching for topic '{topic}': {e}")
    return pd.DataFrame(recommendations.values()).sort_values('stars', ascending=False)

def upload_to_motherduck(df, table_name):
    try:
        conn = get_motherduck_connection()
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
        return conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    except Exception as e:
        print(f"❌ Error uploading to MotherDuck: {e}")
        raise

def main():
    print("🚀 Starting GitHub sync...")
    try:
        starred = get_starred_repos()
        if not starred:
            print("⚠️ No starred repositories found")
            return
        repo_tags, ignore_repos = get_curated_tags()
        starred_df = process_starred_repositories(starred, repo_tags, ignore_repos)
        uploaded = upload_to_motherduck(starred_df, "starred")
        print(f"✅ Uploaded {uploaded} starred repositories")

        recs_df = generate_recommendations(starred_df, ignore_repos)
        if not recs_df.empty:
            uploaded_recs = upload_to_motherduck(recs_df, "recommendations")
            print(f"✅ Uploaded {uploaded_recs} recommendations")
        else:
            print("⚠️ No recommendations generated")

        print("🎉 GitHub sync completed successfully!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()