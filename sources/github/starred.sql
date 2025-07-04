-- Query unified starred repositories data from Google Sheets
-- Combines all starred repos with detailed GitHub data and curated list tags
-- This serves as both a portfolio showcase and comprehensive repository analysis
SELECT 
    name,
    description,
    stars,
    forks,
    language,
    url,
    last_release,
    topics,
    curated_tags,
    all_tags,
    tags_count,
    is_curated,
    created_at,
    updated_at,
    pushed_at,
    open_issues,
    archived,
    fork,
    fetched_at
FROM github.github_data_starred
ORDER BY stars DESC