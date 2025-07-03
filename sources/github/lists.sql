-- Query all GitHub lists repositories data from Google Sheets
-- This contains repositories from curated lists with associated tags
SELECT 
    name,
    description,
    stars,
    forks,
    language,
    url,
    updated_at,
    tags,
    tags_count,
    fetched_at
FROM github.github_data_lists
ORDER BY stars DESC