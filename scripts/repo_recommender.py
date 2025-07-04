'''
GitHub Repository Recommender
Recommends GitHub repositories based on user's starred repositories topics.
Optimized for speed and relevance.
Now uses MotherDuck (cloud DuckDB) for data storage.
'''

import os
import sys
import time
import duckdb
import requests
import pandas as pd
from dotenv import load_dotenv
from collections import Counter

# Import our lists configuration for ignore list
from lists_config import GITHUB_LISTS

# === CONFIGURATION ===
load_dotenv()
GHUB_TOKEN = os.getenv('GHUB_TOKEN')
MOTHERDUCK_TOKEN = os.getenv('MOTHERDUCK_TOKEN')
MOTHERDUCK_DB = os.getenv('MOTHERDUCK_DB', 'github')  # Default database name

auth_headers = {
    'Authorization': f'token {GHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
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

def get_starred_repos_from_motherduck():
    """Read starred repositories from MotherDuck"""
    print(f"📊 Reading starred repositories from MotherDuck")
    
    try:
        conn = get_motherduck_connection()
        
        # Get starred repositories data
        query = "SELECT * FROM starred"
        df = conn.execute(query).df()
        
        conn.close()
        
        print(f"✅ Read {len(df)} rows from starred table")
        return df
        
    except Exception as e:
        print(f"❌ Error reading from MotherDuck: {type(e).__name__}: {e}")
        raise

def get_ignore_repos():
    """Get the list of repositories to ignore from the ignore list"""
    print("🚫 Getting ignore list...")
    
    try:
        # Import the scraper function from starred_fetcher
        from starred_fetcher import scrape_github_list
        
        ignore_config = GITHUB_LISTS.get('ignore')
        if not ignore_config:
            print("⚠️ No ignore list found in configuration")
            return set()
        
        ignore_repos = scrape_github_list(ignore_config['url'], 'ignore')
        ignore_set = set(ignore_repos)
        
        print(f"🚫 Found {len(ignore_set)} repositories to ignore")
        return ignore_set
        
    except Exception as e:
        print(f"❌ Error getting ignore list: {e}")
        return set()

def extract_topic_frequencies(df_starred):
    """Extract and count topic frequencies from starred repositories"""
    print("🔍 Analyzing topics from starred repositories...")
    
    all_topics = []
    starred_repo_full_names = set()
    
    for _, row in df_starred.iterrows():
        # Collect starred repo full names for filtering (owner/repo format)
        if pd.notna(row.get('name')):
            starred_repo_full_names.add(row['name'])
        
        # Extract topics
        topics_str = row.get('topics', '')
        if pd.notna(topics_str) and topics_str.strip():
            topics = [t.strip().lower() for t in topics_str.split(',') if t.strip()]
            all_topics.extend(topics)
    
    # Count topic frequencies
    topic_counter = Counter(all_topics)
    
    print(f"📈 Found {len(topic_counter)} unique topics from {len(df_starred)} starred repos")
    print(f"🔍 Tracking {len(starred_repo_full_names)} starred repositories for filtering")
    for topic, count in topic_counter.most_common(10):
        print(f"  • {topic}: {count} repos")
    
    return topic_counter, starred_repo_full_names

def search_repositories_by_topic(topic, min_stars=1000, max_results=50):
    """Search GitHub repositories by a specific topic"""
    print(f"🔎 Searching for topic: '{topic}' (min {min_stars} stars)")
    
    repositories = []
    per_page = 100
    max_pages = (max_results // per_page) + 1
    
    for page in range(1, max_pages + 1):
        query = f"topic:{topic} stars:>={min_stars}"
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': per_page,
            'page': page
        }
        
        try:
            response = requests.get('https://api.github.com/search/repositories', 
                                  headers=auth_headers, params=params)
            
            if response.status_code != 200:
                print(f"⚠️ API error for topic '{topic}': {response.status_code}")
                break
            
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                break
                
            repositories.extend(items)
            print(f"  📦 Page {page}: {len(items)} repos (total: {len(repositories)})")
            
            # Stop if we have enough results
            if len(repositories) >= max_results:
                repositories = repositories[:max_results]
                break
                
            # Rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Error searching for topic '{topic}': {e}")
            break
    
    print(f"✅ Found {len(repositories)} repositories for topic '{topic}'")
    return repositories

def get_recommendations(topic_counter, starred_repo_full_names, ignore_repos, min_stars=1000, max_per_topic=50):
    """Get repository recommendations based on topic frequencies"""
    print("🎯 Generating recommendations based on topic analysis...")
    
    all_recommendations = {}
    filtered_count = 0
    ignored_count = 0
    
    # Process topics in order of frequency (most common first)
    for topic, frequency in topic_counter.most_common():
        print(f"\n--- Processing topic: '{topic}' (appears in {frequency} starred repos) ---")
        
        repos = search_repositories_by_topic(topic, min_stars, max_per_topic)
        
        for repo in repos:
            repo_id = repo['id']
            repo_full_name = repo['full_name']  # This is "owner/repo" format
            
            # Skip if already starred (check against full_name)
            if repo_full_name in starred_repo_full_names:
                filtered_count += 1
                print(f"  🔄 Skipping already starred: {repo_full_name}")
                continue
            
            # Skip if in ignore list
            if repo_full_name in ignore_repos:
                ignored_count += 1
                print(f"  🚫 Skipping ignored repository: {repo_full_name}")
                continue
            
            # If we haven't seen this repo before, add it
            if repo_id not in all_recommendations:
                all_recommendations[repo_id] = {
                    'repo_data': repo,
                    'topic_matches': [],
                    'total_frequency': 0
                }
            
            # Add this topic match
            all_recommendations[repo_id]['topic_matches'].append(topic)
            all_recommendations[repo_id]['total_frequency'] += frequency
    
    print(f"\n✅ Found {len(all_recommendations)} unique recommendations")
    print(f"🔄 Filtered out {filtered_count} already-starred repositories")
    print(f"🚫 Filtered out {ignored_count} ignored repositories")
    return all_recommendations

def format_recommendations(recommendations_dict):
    """Format recommendations into a DataFrame sorted by relevance and stars"""
    print("📊 Formatting and ranking recommendations...")
    
    formatted_recommendations = []
    
    for repo_id, data in recommendations_dict.items():
        repo = data['repo_data']
        topic_matches = data['topic_matches']
        total_frequency = data['total_frequency']
        
        formatted_recommendations.append({
            'name': repo['full_name'],
            'description': repo.get('description', ''),
            'stars': repo['stargazers_count'],
            'forks': repo['forks_count'],
            'language': repo.get('language', 'Unknown'),
            'url': repo['html_url'],
            'topics': ', '.join(repo.get('topics', [])),
            'matched_topics': ', '.join(topic_matches),
            'topic_frequency_score': total_frequency,
            'num_topic_matches': len(topic_matches)
        })
    
    df = pd.DataFrame(formatted_recommendations)
    
    # Sort by topic frequency score (descending) and then by stars (descending)
    df = df.sort_values(['topic_frequency_score', 'stars'], ascending=[False, False])
    
    print(f"🏆 Top 10 recommendations:")
    for i, row in df.head(10).iterrows():
        print(f"  {i+1}. {row['name']} ({row['stars']:,} ⭐) - Score: {row['topic_frequency_score']}")
        print(f"     Matched topics: {row['matched_topics']}")
    
    return df

def upload_recommendations_to_motherduck(df, table_name='recommendations'):
    """Upload DataFrame to MotherDuck"""
    print(f"📤 Uploading recommendations to MotherDuck: {table_name}")
    
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
    print("🚀 Starting optimized repository recommendation sync with MotherDuck...")
    
    try:
        # Read starred repositories from MotherDuck
        df_starred = get_starred_repos_from_motherduck()
        
        if df_starred.empty:
            print("⚠️ No starred repositories found in MotherDuck. Cannot generate recommendations.")
            return
        
        # Get ignore list
        ignore_repos = get_ignore_repos()
        
        # Extract topic frequencies and starred repo names
        topic_counter, starred_repo_full_names = extract_topic_frequencies(df_starred)
        
        if not topic_counter:
            print("⚠️ No topics found in starred repositories. Cannot generate recommendations.")
            return
        
        # Get recommendations based on topics
        recommendations_dict = get_recommendations(topic_counter, starred_repo_full_names, ignore_repos)
        
        if not recommendations_dict:
            print("⚠️ No recommendations found.")
            return
        
        # Format and sort recommendations
        df_recommendations = format_recommendations(recommendations_dict)
        
        # Upload recommendations to MotherDuck
        upload_recommendations_to_motherduck(df_recommendations)
        
        print("🎉 Successfully generated and uploaded repository recommendations!")
        print(f"📈 Generated {len(df_recommendations)} recommendations based on {len(topic_counter)} topics")
        print(f"🚫 Ignored {len(ignore_repos)} repositories from ignore list")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 