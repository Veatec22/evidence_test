import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_github_list(list_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(list_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to load page: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    repo_blocks = soup.select('div#user-list-repositories > div.border-bottom')

    data = []
    for block in repo_blocks:
        name_tag = block.select_one('h3 a')
        full_name = name_tag['href'].strip('/') if name_tag else 'N/A'
        repo_url = f"https://github.com/{full_name}"

        desc_tag = block.select_one('[itemprop=description]')
        description = desc_tag.text.strip() if desc_tag else ''

        lang_tag = block.select_one('[itemprop=programmingLanguage]')
        language = lang_tag.text.strip() if lang_tag else ''

        stars_tag = block.select_one('a[href$="/stargazers"]')
        stars = stars_tag.text.strip().replace(',', '') if stars_tag else '0'

        forks_tag = block.select_one('a[href$="/forks"]')
        forks = forks_tag.text.strip().replace(',', '') if forks_tag else '0'

        updated_tag = block.select_one('relative-time')
        updated = updated_tag['datetime'] if updated_tag else ''

        data.append({
            'name': full_name,
            'url': repo_url,
            'description': description,
            'language': language,
            'stars': int(stars),
            'forks': int(forks),
            'updated_at': updated
        })

    return pd.DataFrame(data)

# Example usage:
df_list = scrape_github_list("https://github.com/stars/Veatec22/lists/stack")
print(df_list.head())
